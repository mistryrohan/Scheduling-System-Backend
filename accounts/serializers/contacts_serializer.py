from rest_framework import serializers
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from calendars.models import contact_model
from rest_framework.exceptions import ValidationError


class ContactsSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = contact_model.Contact
        fields = ['email']

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise ValidationError("No user found with this email address.")
        return value

    # def to_representation(self, instance):  # read from documentations to return the user2 data
    #     representation = {
    #         'id': instance.user2.id,
    #         'username': instance.user2.username,
    #         'first_name': instance.user2.first_name,
    #         'last_name': instance.user2.last_name,
    #         'email': instance.user2.email,
    #     }
    #     return representation

    def to_representation(self, instance):
        # request_user = self.context.get('request_user')
        request_user = self.context['request'].user
        # Determine the other user in the contact relationship
        other_user = instance.user2 if instance.user1 == request_user else instance.user1
        representation = {
            'id': other_user.id,
            'username': other_user.username,
            'first_name': other_user.first_name,
            'last_name': other_user.last_name,
            'email': other_user.email,
        }
        return representation

    def create(self, validated_data):
        email = validated_data.pop('email', None)
        user2 = User.objects.filter(email=email).first()

        if not user2:
            raise ValidationError("No user found with this email address.")

        contact = contact_model.Contact.objects.create(
            user1=self.context['request'].user,
            user2=user2
        )
        return contact