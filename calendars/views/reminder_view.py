from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from calendars.models.calendar_model import Calendar
from calendars.serializers.invitee_serializer import InviteeSerializer


class ReminderView(APIView):
    """
    POST: send a reminder to the user about the related calendar.
    """
    permission_classes = [IsAuthenticated]

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
                return Response({
                    "invitation": serializer.data,
                    "message": "Invitation sent successfully"
                }, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def construct_email(self, calendar, user):
        if calendar.primary_user.first_name != "":
            subject = "Reminder to Respond to " + calendar.primary_user.first_name + "'s Calendar Invitation."
            main_text = calendar.primary_user.first_name + " is still waiting for your response!"
        else:
            subject = "Reminder to Respond to Calendar Invitation."
            main_text = "Please be reminded to respond to your calendar invitation.\n"

        if user.first_name != "":
            greeting = "Hi " + user.first_name + ",\n"
        else:
            greeting = "Hi,\n"

        link = "http://127.0.0.1:8000/calendars/" + str(calendar.pk) + "/invitee/" + str(user.pk) + "/"

        return {
            "subject": subject,
            "body": greeting + main_text + "You can respond with your availability at the following link: " + link
        }

        