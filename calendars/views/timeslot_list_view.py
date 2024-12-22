from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from calendars.models.calendar_model import Calendar
from calendars.models.invitee_model import Invitee
from calendars.models.timeslot_model import Timeslot
from calendars.serializers.timeslot_serializer import TimeslotSerializer
from rest_framework.exceptions import PermissionDenied

class TimeslotListView(APIView):
    """
    GET: see the timeslots for a given calendar_id.
    POST: add a timeslot to the calendar.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, calendar_id):
                
        try:
            calendar = get_object_or_404(Calendar, id=calendar_id)
            # if calendar.primary_user != request.user:
            #     raise PermissionDenied
        except Http404:
            return Response({
                "message": "Calendar not found."
            }, status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({
                "message": "User is not the owner of the calendar."
            }, status.HTTP_403_FORBIDDEN)
        
        timeslots = Timeslot.objects.filter(calendar_id=calendar_id)
        serializer = TimeslotSerializer(timeslots, many=True)
        return Response(serializer.data)

    def post(self, request, calendar_id):
        try:
            calendar = get_object_or_404(Calendar, id=calendar_id)
            # if calendar.primary_user != request.user and not Invitee.objects.filter(calendar_id=calendar_id, user=request.user).exists():
            #     raise PermissionDenied
            # if not Invitee.objects.filter(calendar_id=calendar_id, user=request.user).exists():
            #     raise PermissionDenied
        except Http404:
            return Response({
                "message": "Calendar not found."
            }, status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({
                "message": "User is not a member of the calendar."
            }, status.HTTP_403_FORBIDDEN)
        
        # if 'timeslots' not in data:
        #     raise ValidationError("Timeslots required.")
        
        timeslots_data = []
        serializers = []
        data = request.data.copy()
        for slot_data in data['timeslots']: 
            slot_data['user'] = request.user.id
            slot_data['calendar'] = calendar_id
            
            serializer = TimeslotSerializer(data=slot_data)
            if serializer.is_valid():
                serializers.append(serializer)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        for serializer in serializers:
            serializer.save()
            timeslots_data.append(serializer.data) 
        
        return Response({
            "meetings": timeslots_data, 
            "message": "All timeslots created successfully."
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, calendar_id):
        user = request.user
        try:
            calendar = get_object_or_404(Calendar, id=calendar_id)
            timeslot = Timeslot.objects.filter(calendar=calendar, user=user.pk)
            if not timeslot:
                return Response({
                    "message": "No timeslots found to delete"
                })
        except Http404:
            return Response({
                "message": "Calendar not found"
            }, status.HTTP_404_NOT_FOUND)
        except Timeslot.DoesNotExist:
            return Response({
                "message": "No timeslots found to delete"
            }, status.HTTP_404_NOT_FOUND)

        timeslot.delete()
        return Response({
            "message": "timeslots for user " + str(user.pk) + " in calendar " + str(calendar_id) + " were deleted"
        })
