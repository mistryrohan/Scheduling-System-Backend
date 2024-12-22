from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from calendars.models.calendar_model import Calendar
from calendars.models.invitee_model import Invitee
from meetings.models.meeting_model import Meeting
from calendars.serializers.calendar_serializer import CalendarSerializer
from django.contrib.auth.models import User
import datetime

class CalendarListView(APIView):
    """
    GET: list of the calendars owned by user.
    POST: create a new calendar.
    """
    permission_classes = [IsAuthenticated]
 
    def get(self, request):
        user = request.user
        
        owned_calendars = Calendar.objects.filter(primary_user=user)
        owned_serializer = CalendarSerializer(owned_calendars, many=True)
        
        invitee_calendars = Invitee.objects.filter(user=user)
        invitee_serializer = CalendarSerializer([invitee.calendar for invitee in invitee_calendars], many=True)
        
        for calendars in [owned_serializer.data, invitee_serializer.data]:
            for calendar in calendars:
                has_meeting = Meeting.objects.filter(calendar=calendar['id']).exists()
                respondants = User.objects.filter(timeslot__calendar=calendar['id']).distinct()
                invitees = Invitee.objects.filter(calendar=calendar['id']).distinct()
                
                calendar['has_meeting'] = has_meeting
                calendar['respondants'] = list(respondants.values_list('id', flat=True))
                calendar['all_responded'] = invitees.count() == respondants.count() - 1
        
        return Response({
            "owned_calendars": owned_serializer.data,
            "invitee_calendars": invitee_serializer.data
        })
    
    def post(self, request):
        calendar = request.data.copy()
        calendar['primary_user'] = request.user.pk
        serializer = CalendarSerializer(data=calendar)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "calendar": serializer.data,
                "message": "Calendar created successfully."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)