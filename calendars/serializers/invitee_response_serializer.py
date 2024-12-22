from rest_framework import serializers
from calendars.models.invitee_model import Invitee

class InviteeResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitee
        fields = ['status', 'responded']
        extra_kwargs = {
            'status': {'required': True},
            'resonded': {'read_only': True}
        }
        
    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.responded = True  
        instance.save()
        return instance
        
    