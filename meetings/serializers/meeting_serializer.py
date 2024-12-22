from rest_framework import serializers
from calendars.models.calendar_model import Calendar
from calendars.serializers.calendar_serializer import CalendarSerializer
from meetings.models.meeting_model import Meeting
from django.contrib.auth.models import User

class MeetingPostSerializer(serializers.ModelSerializer):
    calendar = CalendarSerializer()  # Include calendar object alongside Meeting

    class Meta:
        model = Meeting
        fields = ['id', 'user', 'start_time', 'duration', 'calendar']

    def create(self, validated_data):
        calendar = validated_data.pop('calendar')
        meeting = Meeting.objects.create(calendar=calendar, **validated_data)
        return meeting


class MeetingCreateSerializer(serializers.ModelSerializer):
    calendar_id = serializers.PrimaryKeyRelatedField(queryset=Calendar.objects.all(), write_only=True, source='calendar')

    class Meta:
        model = Meeting
        fields = ['id', 'user', 'start_time', 'duration', 'calendar', 'calendar_id']

    def update(self, instance, validated_data):
        instance.user = validated_data.get('user', instance.user)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.duration = validated_data.get('duration', instance.duration)

        calendar_id = validated_data.get('calendar_id', instance.calendar_id)
        calendar = Calendar.objects.get(pk=calendar_id)
        instance.calendar = calendar

        instance.save()
        return instance
