from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from calendars.models.calendar_model import Calendar
from calendars.serializers.calendar_serializer import CalendarSerializer
from rest_framework.exceptions import PermissionDenied

class CalendarDetailView(APIView):
    """
    GET: Retrieve the current calendar.
    PUT: Update calendar.
    DELETE: Delete calendar.
    """
    permission_classes = [IsAuthenticated]

 
    def get(self, request, calendar_id):
        
        try:
            calendar = get_object_or_404(Calendar, id=calendar_id)
            if calendar.primary_user != request.user:
                raise PermissionDenied
        except Http404:
            return Response({"message": "Calendar not found."}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({"message": "User is not the owner of the calendar."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CalendarSerializer(calendar, many=False)
        return Response(serializer.data)
    
    def put(self, request, calendar_id):
        
        try:
            calendar = get_object_or_404(Calendar, id=calendar_id)
            if calendar.primary_user != request.user:
                raise PermissionDenied
        except Http404:
            return Response({"message": "Calendar not found."}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({"message": "User is not the owner of the calendar."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CalendarSerializer(calendar, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "calendar": serializer.data,
                "message": "Calendar updated successfully."
            }, status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, calendar_id):
        
        try:
            calendar = get_object_or_404(Calendar, id=calendar_id)
            if calendar.primary_user != request.user:
                raise PermissionDenied
        except Http404:
            return Response({"message": "Calendar not found."}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({"message": "User is not the owner of the calendar."}, status=status.HTTP_403_FORBIDDEN)
        
        success, _ = calendar.delete()
        if success:
            return redirect(reverse_lazy('calendars:calendar_list_view'))
        return Response({
            "message": "No calendar was deleted."
        }, status.HTTP_500_INTERNAL_SERVER_ERROR)