from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from calendars.serializers.invitee_serializer import InviteeSerializer

from calendars.models.calendar_model import Calendar

from calendars.models.contact_model import Contact

from calendars.models.invitee_model import Invitee


class InvitationView(APIView):
    """
    POST: invite user(s) from the user_ids array to the meeting as secondary users.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, calendar_id):
        try:
            calendar = get_object_or_404(Calendar, id=calendar_id)
        except Http404:
            return Response({"message": "Calendar not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            invited_users = Invitee.objects.filter(calendar=calendar)
            if not invited_users:
                raise Invitee.DoesNotExist
        except Invitee.DoesNotExist:
            return Response({"message": "No invitations were sent for this calendar yet"})

        # Added a new response with the users included
        responded_invitees = invited_users.filter(responded=True)
        num_responded = responded_invitees.count()
        responded_invitees_serializer = InviteeSerializer(responded_invitees, many=True)
        
        # Response has users now
        return Response({
            "count_responded": num_responded,
            "responded_invitees_details": responded_invitees_serializer.data,
            "message": f"{num_responded} contacts have responded to the invitation for this calendar"
        }, status=status.HTTP_200_OK)

    def post(self, request, calendar_id):
        if "users" not in request.data:
            return Response({"message": "users is a required field"}, status=status.HTTP_404_NOT_FOUND)

        user_ids = request.data['users']
        for user_id in user_ids:
            try:
                calendar = get_object_or_404(Calendar, id=calendar_id)
            except Http404:
                return Response({"message": "Calendar not found."}, status=status.HTTP_404_NOT_FOUND)

            try:
                user = get_object_or_404(User, id=user_id)
            except Http404:
                return Response({"message": "user not found"}, status=status.HTTP_404_NOT_FOUND)

            data = {
                "user": user_id,
                "calendar": calendar_id,
            }
            serializer = InviteeSerializer(data=data)
            if serializer.is_valid():
                email = self.construct_email(calendar, user)
                send_mail(
                    subject=email['subject'],
                    message=email['body'],
                    from_email="csc309p2@gmail.com",
                    recipient_list=[user.email]
                )
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "message": "Invitations sent successfully"
        }, status=status.HTTP_201_CREATED)

    def construct_email(self, calendar, user):

        if calendar.primary_user.first_name != "":
            subject = "New Invitation For " + calendar.primary_user.first_name + "'s Calendar."
            main_text = "You've been invited to " + calendar.primary_user.first_name + "'s Calendar.\n"
        else:
            subject = "New Calendar Invitation!"
            main_text = "You've been invited to a Calendar!\n"

        if user.first_name != "":
            greeting = "Hi " + user.first_name + ",\n"
        else:
            greeting = "Hi,\n"

        link = "http://127.0.0.1:3000/calendars/" + str(calendar.pk) +"/invitee/" + str(user.pk) + "/"

        return {
            "subject": subject,
            "body": greeting + main_text + "Please use the following link to respond with your availability: " + link
        }


