from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from calendars.models.calendar_model import Calendar
from calendars.models.invitee_model import Invitee
from calendars.models.timeslot_model import Timeslot
from calendars.serializers.timeslot_serializer import TimeslotSerializer
from rest_framework.exceptions import PermissionDenied

class TimeslotDetailView(APIView):
    """
    GET: View given timeslot.
    PUT: Update a timeslot.
    DELETE: Delete a timeslot.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, timeslot_id):
        
        try:
            timeslot = get_object_or_404(Timeslot, id=timeslot_id)
            calendar = timeslot.calendar
            if calendar.primary_user != request.user and not Invitee.objects.filter(calendar_id=calendar.id, user=request.user).exists():
                raise PermissionDenied
        except Http404:
            return Response({
                "message": "Timeslot not found."
            }, status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({
                "message": "User is not a member of the calendar."
            }, status.HTTP_403_FORBIDDEN)
        
        timeslots = Timeslot.objects.filter(id=timeslot_id)
        serializer = TimeslotSerializer(timeslots, many=True)
        return Response(serializer.data)

    def put(self, request, timeslot_id):
        
        try:
            timeslot = get_object_or_404(Timeslot, id=timeslot_id)
            if timeslot.user != request.user:
                raise PermissionDenied
        except Http404:
            return Response({
                "message": "Timeslot not found."
            }, status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({
                "message": "User is not the owner of the timeslot."
            }, status.HTTP_403_FORBIDDEN)
        
        serializer = TimeslotSerializer(timeslot, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "timeslot": serializer.data,
                "message": "Timeslot updated successfully."
            }, status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, timeslot_id):
        
        try:
            timeslot = get_object_or_404(Timeslot, id=timeslot_id)
            if timeslot.user != request.user:
                raise PermissionDenied
        except Http404:
            return Response({
                "message": "Timeslot not found."
            }, status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({
                "message": "User is not the owner of the timeslot."
            }, status.HTTP_403_FORBIDDEN)
        
        calendar_id = timeslot.calendar.id
        success, _ = timeslot.delete()
        if success:
            return redirect(reverse_lazy('calendars:timeslot_list_view', kwargs={'calendar_id': calendar_id}))
        return Response({
            "message": "No timeslot was deleted."
        }, status.HTTP_500_INTERNAL_SERVER_ERROR)
