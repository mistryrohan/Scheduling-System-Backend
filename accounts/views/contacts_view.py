from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from accounts.serializers import contacts_serializer
from rest_framework.permissions import IsAuthenticated
from calendars.models import contact_model
from django.contrib.auth.models import User
from django.db.models import Q

class ContactsView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = contacts_serializer.ContactsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            user2 = User.objects.filter(email=email).first()
            if user2 is None:
                return Response({"message": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)
            if user2 == self.request.user:
                return Response({"message": "Can not add yourself as a contact."}, status=status.HTTP_404_NOT_FOUND)
            contacts = contact_model.Contact.objects.filter(user1=self.request.user, user2=user2)
            if contacts.exists():
                return Response({"message": "Contact already exists."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                contact = serializer.save()
                return Response({
                    "contact": contacts_serializer.ContactsSerializer(contact, context={'request': request}).data,
                    "message": "Contact created sucessfully"
                })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):
        # Fetch contacts where request.user is either user1 or user2
        contacts = contact_model.Contact.objects.filter(
            Q(user1=request.user) | Q(user2=request.user)
        )
        serializer = contacts_serializer.ContactsSerializer(contacts, many=True, context={'request': request})
        return Response(serializer.data)

    def delete(self, request):
        user2 = request.data.get('user2')
        contact = get_object_or_404(contact_model.Contact, user1=request.user, user2=user2)
        contact.delete()
        return Response({"message": "Contact deleted sucessfully"})