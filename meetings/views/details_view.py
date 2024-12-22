from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from meetings.models.meeting_model import Meeting
from rest_framework.permissions import IsAuthenticated
from meetings.serializers.meeting_serializer import MeetingPostSerializer
from django.contrib.auth.models import User

class DetailsView(APIView):
    """
    GET: View meeting details for the user (times and current priority).
    POST: Update meeting details for the user (start time, end time, and priority).
    PUT:
    DELETE:
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, id=meeting_id)
        serializer = MeetingPostSerializer(meeting)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        serializer = MeetingPostSerializer(meeting, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



            