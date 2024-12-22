from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from meetings.models.meeting_model import Meeting
from calendars.models.calendar_model import Calendar
from meetings.serializers.meeting_serializer import MeetingPostSerializer

class MeetingsView(APIView):
    permission_classes = [IsAuthenticated]
    
    """
    GET: list of user's scheduled meetings.
    """
    def get(self, request):
        user = request.user
        hosted_meetings = Meeting.objects.filter(calendar__primary_user=user)
        invited_meetings = Meeting.objects.filter(calendar__invitee__user=user).distinct()

        
        # TODO added
        invited_meetings_serialized = MeetingPostSerializer(invited_meetings, many=True).data
        invited_meetings_ids = [meeting['id'] for meeting in invited_meetings_serialized]

        actual_invited_meetings = []
        for meeting in invited_meetings:
            if meeting.user.pk != user.pk:
                actual_invited_meetings.append(meeting)

        
        response = {
            "hosted_meetings": MeetingPostSerializer(hosted_meetings, many=True).data,
            "invited_meetings": MeetingPostSerializer(actual_invited_meetings, many=True).data,
            "meeting_id": invited_meetings_ids
        }
        
        return Response(response)
    