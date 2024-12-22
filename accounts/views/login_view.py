from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from accounts.serializers import login_serializer
from rest_framework_simplejwt.tokens import RefreshToken

class LoginView(APIView):
    def post(self, request):
        serializer = login_serializer.LoginSerializer(data=request.data) 
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            if user is None:
                return Response({"message": ["Username or password is invalid"]}, status=status.HTTP_400_BAD_REQUEST)
            login(request, user)
            refresh_token = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh_token),
                "access": str(refresh_token.access_token),
                "user": serializer.data,
                "id": user.id,
                "message": "User Logged In"
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
