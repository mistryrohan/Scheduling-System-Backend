from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.serializers import profile_serializer

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "password1": "",
                "password2": ""
            }
        })

    def put(self, request):
        user = request.user
        serializer = profile_serializer.ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "user": serializer.data,
                "message": "User updated sucessfully"
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)