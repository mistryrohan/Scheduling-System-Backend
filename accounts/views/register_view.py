from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.serializers import register_serializer

class RegisterView(APIView):
    def post(self, request):
        serializer = register_serializer.RegisterSerializer(data=request.data) 
        
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": serializer.data,
                "message": "User created sucessfully"
            })  
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)