from datetime import timedelta
from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from calendars.models.calendar_model import Calendar
from calendars.models.invitee_model import Invitee
from calendars.models.timeslot_model import Timeslot
from calendars.serializers.calendar_serializer import CalendarSerializer
from meetings.models.meeting_model import Meeting
from meetings.serializers.meeting_serializer import MeetingCreateSerializer
from django.contrib.auth.models import User
from django.core.mail import send_mail
from datetime import timedelta


# this algorithm prioritizes having meetings for everyone rather than maximizing it.
# ideally, it would be checking the priority level as well, but it introduces complication im not willing to do for this lol
def resolve_conflicts(all_meetings):
    
    def conflicts(slot, other_slot):
        start = slot["time"]
        end = start + timedelta(minutes=slot["duration"])

        other_start = other_slot["time"]
        other_end = other_start + timedelta(minutes=other_slot["duration"])
        
        return not (end <= other_start or start >= other_end) or (end == other_end and start == other_start)
    

    for i, meeting in enumerate(all_meetings):
        selected_timeslot = meeting["timeslots"][meeting["selected"]]
        for j, other_meeting in enumerate(all_meetings):
            if i != j:  # For each meeting timeslot and all other timeslots
                other_selected_timeslot = other_meeting["timeslots"][other_meeting["selected"]]
                if conflicts(selected_timeslot, other_selected_timeslot):
                    
                    # if meeting has more/same alternative timeslots than other_meeting
                    if other_meeting["selected"]  >= 0 and len(meeting["timeslots"]) - meeting["selected"] <= len(other_meeting["timeslots"]) - other_meeting["selected"]:
                        other_meeting["selected"] += 1
                        if other_meeting["selected"] > len(other_meeting):
                            other_meeting["selected"] = -1 # ran out of compatible meetings.
                        
                    # if other_meeting has more alternative timeslots than meeting
                    elif meeting["selected"]  >= 0 and len(other_meeting["timeslots"]) - other_meeting["selected"] <= len(meeting["timeslots"])  - meeting["selected"]:
                        meeting["selected"] += 1
                        if meeting["selected"] > len(meeting):
                            meeting["selected"] = -1 # ran out of compatible meetings.


class FinalizeView(APIView):
    """
    GET: Return the possible Final meeting details for each user in the selected schedule.
    POST: Return the selection and create a Meeting.
    """
    permission_classes = [IsAuthenticated]
    # Post should just expect what the meeting should be. nothing special.
    # 1. GET generates the possible meetings, and sends it to the user.
    # 2. The user selects the meeting, which makes a POST with the data expected to make a POST.
    
    def get(self, request, calendar_id):
        try:
            calendar = get_object_or_404(Calendar, id=calendar_id)
            if calendar.primary_user != request.user:
                return Response({"message": "User is not the owner of the calendar."}, status=status.HTTP_403_FORBIDDEN)
            
            if Meeting.objects.filter(calendar=calendar_id).exists():
                return Response({"message": "Calendar has already been scheduled."}, status=status.HTTP_403_FORBIDDEN)
        except Http404:
            return Response({"message": "Calendar not found."}, status=status.HTTP_404_NOT_FOUND)
        
        incompatible_users = []
        
        # Retrieve a list of all timeslots of the primary_user.
        primary_timeslots = Timeslot.objects.filter(calendar_id=calendar_id, user=request.user).order_by('start_time')
        
        # Retrieve a list of list of timeslots for each invited secondary_user.
        secondary_timeslots_list = [(user_id, list(Timeslot.objects.filter(calendar_id=calendar_id, user=user_id).order_by('start_time'))) for user_id in Invitee.objects.filter(calendar_id=calendar_id).values_list('user', flat=True).distinct()]
        
        # If the primary_user has no timeslots --
        if len(primary_timeslots) < 1:
            return Response({"message": "Owner has not indicated availability."}, status=status.HTTP_400_BAD_REQUEST)

        all_meetings = []
        
        for user_id, secondary_timeslots in secondary_timeslots_list:
            if len(secondary_timeslots) < 1:
                return Response({"message": "User has not indicated availability.", "user": user_id}, status=status.HTTP_400_BAD_REQUEST)
            
            compatible_meetings = []
            
            for primary_timeslot in primary_timeslots:
                for secondary_timeslot in secondary_timeslots:
                    overlap_start = max(primary_timeslot.start_time, secondary_timeslot.start_time)
                    overlap_end = min(primary_timeslot.end_time, secondary_timeslot.end_time)
                    overlap_duration = overlap_end - overlap_start
                    
                    if overlap_duration >= timedelta(minutes=calendar.duration):
                        current_time = overlap_start
                        priority = int(primary_timeslot.priority) + int(secondary_timeslot.priority)
                        
                        while current_time + timedelta(minutes=calendar.duration) <= overlap_end:
                            compatible_meetings.append({"time": current_time, "duration": calendar.duration, "priority": priority})
                            current_time += timedelta(minutes=30)  
            
            if len(compatible_meetings) < 1:
                incompatible_users.append(user_id)
            
            compatible_meetings.sort(key=lambda x: x["priority"], reverse=True)

            user = get_object_or_404(User, id=user_id)
            user_data = {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            }

            all_meetings.append({"user": user_data, "selected": 0, "timeslots": compatible_meetings})
        
        if len(incompatible_users) > 0:
            return Response({"message": "No compatible meetings between primary and secondary users in list.", "users": incompatible_users}, status=status.HTTP_406_NOT_ACCEPTABLE)
            
        resolve_conflicts(all_meetings)
        
        return Response({"calendar": CalendarSerializer(calendar).data, "meetings": all_meetings})
    
    def post(self, request, calendar_id):
        try:
            calendar = get_object_or_404(Calendar, id=calendar_id)
            if calendar.primary_user != request.user:
                raise PermissionDenied
        except Http404:
            return Response({
                "message": "Calendar not found."
            }, status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({
                "message": "User is not the owner of the calendar."
            }, status.HTTP_403_FORBIDDEN)
        
        # if 'meetings' not in data:
        #     raise ValidationError("Meetings required.")
        
        meetings = []
        serializers = []
        data = request.data.copy()
        for meeting in data['meetings']:
            meeting['calendar'] = calendar_id
            
            try:
                user = get_object_or_404(User, id=request.user.id)
            except Http404:
                return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = MeetingCreateSerializer(data=meeting)
            if serializer.is_valid():
                serializers.append(serializer)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        for serializer in serializers:
            serializer.save()
            meeting = serializer.data
            meetings.append(meeting)
            # send_mail(
            #      subject="Your meeting has been scheduled.",
            #      message = f"Your meeting has been scheduled. Please check OneOnOne for details",
            #      from_email="csc309p2@gmail.com",
            #      recipient_list=[user.email])
        
        return Response({
            "meetings": meetings,
            "message": "All meetings created successfully."
        }, status=status.HTTP_201_CREATED)
     