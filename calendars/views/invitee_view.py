from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from calendars.models.calendar_model import Calendar
from calendars.models.invitee_model import Invitee
from calendars.serializers.calendar_serializer import CalendarSerializer
from calendars.serializers.invitee_serializer import InviteeSerializer
from calendars.serializers.invitee_response_serializer import InviteeResponseSerializer 


class InviteeView(APIView):
    """
    GET: A landing page for the invites to view the calendar details and respond to invitations.
    """
    def get(self, request, calendar_id, user_id):  
        calendar = get_object_or_404(Calendar, id=calendar_id)
        
        try:
            invitee = Invitee.objects.get(calendar=calendar, user_id=user_id) 
        except:
            return Response({"message": "Invitation not found for this user in specified calendar"}, status=status.HTTP_404_NOT_FOUND) 
        
        calendar_serialzer = CalendarSerializer(calendar, many=False)
        invitee_serializer = InviteeSerializer(invitee, many=False)
        
        response_data = {
            "calendar": calendar_serialzer.data,
            "invitee_status": invitee_serializer.data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def post(self, request, calendar_id, user_id):
        calendar = get_object_or_404(Calendar, id=calendar_id)
        invitee = get_object_or_404(Invitee, calendar=calendar, user_id=user_id)
        
        response = request.data.get('response', None)
        if response not in [choice[0] for choice in Invitee.STATUS_CHOICES]:
            return Response({"message": "Invalid response"}, status=status.HTTP_400_BAD_REQUEST)
        
        invitee.status = response
        invitee.responded = True
        invitee.save()
        
        return Response({"message": "Your response has been recorded successfully"}, status=status.HTTP_200_OK)
    
    def put(self, request, calendar_id, user_id):
        invitee = get_object_or_404(Invitee, calendar_id=calendar_id, user_id=user_id)
        serialzer = InviteeResponseSerializer(invitee, data=request.data, partial=True)
        
        if serialzer.is_valid():
            serialzer.save()
            return Response(serialzer.data, status=status.HTTP_200_OK)
        else:
            return Response(serialzer.errors, status=status.HTTP_400_BAD_REQUEST)