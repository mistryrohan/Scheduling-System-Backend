from django.forms import ValidationError
from rest_framework import serializers
from django.contrib.auth.models import User
from calendars.models.calendar_model import Calendar

class CalendarSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Calendar 
        fields = ['id', 'primary_user', 'name', 'description', 'duration']

    def create(self, validated_data):
        """
        Create and return a new `Calendar` instance.
        """
        return Calendar.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Calendar` instance.
        """
        if 'name' in validated_data:
            instance.name = validated_data.get('name', instance.name)
            
        if 'description' in validated_data:
            instance.description = validated_data.get('description', instance.description)
            
        if 'duration' in validated_data:
            duration = int(validated_data.get('duration', instance.duration))
            if duration % 30 != 0:
                raise ValidationError("Duration must be divisible by 30 minutes.")
            instance.duration = duration
            
        instance.save()
        return instance
