from rest_framework import serializers
from django.contrib.auth.models import User
from calendars.models.calendar_model import Calendar
from calendars.models.timeslot_model import Timeslot

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class TimeslotSerializer2(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Timeslot
        fields = ['id', 'start_time', 'end_time', 'priority', 'calendar', 'user']
    
    def create(self, validated_data):
        """
        Create and return a new `Timeslot` instance.
        """
        start_time = validated_data['start_time']
        end_time = validated_data['end_time']
        
        if start_time > end_time:
            raise serializers.ValidationError({"start_time": "End time must be greater than start time."})

        if start_time.minute not in [0, 30] and start_time.second != 0:
            raise serializers.ValidationError({"start_time": "Timeslots must begin at the half-hour or hour mark and have 0 seconds."})

        if end_time.minute not in [0, 30] and end_time.second != 0:
            raise serializers.ValidationError({"end_time": "Timeslots must begin at the half-hour or hour mark and have 0 seconds."})

        return Timeslot.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Timeslot` instance.
        """
        
        start_time = validated_data.get('start_time', instance.start_time) if 'start_time' in validated_data else instance.start_time
        end_time = validated_data.get('end_time', instance.start_time) if 'end_time' in validated_data else instance.end_time
        
        if start_time > end_time:
            raise serializers.ValidationError({"start_time": "End time must be greater than start time."})

        if start_time.minute not in [0, 30] and start_time.second != 0:
            raise serializers.ValidationError({"start_time": "Timeslots must begin at the half-hour or hour mark and have 0 seconds."})

        if end_time.minute not in [0, 30] and end_time.second != 0:
            raise serializers.ValidationError({"end_time": "Timeslots must begin at the half-hour or hour mark and have 0 seconds."})

        instance.start_time = start_time
        instance.end_time = end_time
        
        if 'priority' in validated_data:
            instance.priority = validated_data.get('priority', instance.priority)
            
        instance.save()
        return instance
