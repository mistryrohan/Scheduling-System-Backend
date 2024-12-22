from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    # I read online and got to know that access tokens can not be blacklisted, but refresh tokens can. So,
    # the resources recommended I use refresh tokens for logout.
    def post(self, request):
        refresh_token = request.data.get("refresh")
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "User logged out successfully."})
        except Exception as e:
            return Response({"message": "An error occurred during logout."}, status=status.HTTP_400_BAD_REQUEST)