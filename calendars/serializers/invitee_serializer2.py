from rest_framework import serializers
from calendars.models.calendar_model import Calendar
from calendars.models.invitee_model import Invitee
from calendars.models.contact_model import Contact
from django.contrib.auth.models import User

# New added for details view
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class InviteeSerializer2(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Invitee
        fields = ['id', 'user', 'responded', 'status', 'calendar']
        
    def validate(self, attrs):
        user = attrs.get('user')
        primary_user = attrs.get('calendar').primary_user

        try:
            contact = Contact.objects.filter(user1=user, user2=primary_user) \
                      | Contact.objects.filter(user1=primary_user, user2=user)
            if not contact:
                raise Contact.DoesNotExist
            print(contact)
        except Contact.DoesNotExist:
            raise serializers.ValidationError({"message": "User is not a contact of the Calendar's primary user"})

        return attrs

    def create(self, validated_data):
        """
        Create and return a new `Invitee` instance.
        """
        return Invitee.objects.create(**validated_data)
