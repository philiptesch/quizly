from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics, status
from .seralizers import RegistrationSerializer, LoginSeralizer
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class RegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.

    Permissions:
        - Public endpoint (no authentication required).

    Behavior:
        - POST:
            - Validates registration data using RegistrationSerializer.
            - Creates a new user account.
            - Returns a success message on successful registration.
            - Returns validation errors if input data is invalid.
    """

    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "User created successfully!"}, status=status.HTTP_201_CREATED)
        
        else: 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginCookieView(TokenObtainPairView):
    """
    API endpoint for user login using JWT stored in HTTP-only cookies.

    Permissions:
        - Public endpoint (no authentication required).

    Behavior:
        - POST:
            - Validates user credentials.
            - Returns user info on success.
            - Stores access and refresh tokens in secure HTTP-only cookies.
            - Returns 401 if authentication fails.
    """
    
    serializer_class = LoginSeralizer

    def post(self, request, *args, **kwargs):
        seralizer = self.get_serializer(data=request.data)
        if not seralizer.is_valid():
            return Response(seralizer.errors, status=status.HTTP_401_UNAUTHORIZED)
        refresh = seralizer.validated_data['refresh']
        access = seralizer.validated_data['access']
        response = Response({"detail": "Login successfully!","user": {'id': seralizer.user.id,'username': seralizer.user.username,'email': seralizer.user.email}},status=status.HTTP_200_OK)

        response.set_cookie(
            key="access_token", value=access, httponly=True, secure=True, samesite="Lax")
        
        response.set_cookie(
            key="refresh_token", value=refresh, httponly=True, secure=True, samesite="Lax")
        return response
    

class LogoutView(APIView):
    """
    API endpoint for logging out a user.

    Permissions:
        - User must be authenticated.

    Behavior:
        - POST:
            - Deletes access and refresh token cookies.
            - Returns a success message.
            - Returns 400 if no access token cookie is found.
    """

    permission_classes = [IsAuthenticated]


    def post(self, request, *args, **kwargs):

        access_token = request.COOKIES.get("access_token")
        if access_token is None:
            return Response({"detail": "access_token not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        response = Response({"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."}, status=status.HTTP_200_OK)

        response.delete_cookie(key='refresh_token')
        response.delete_cookie(key='access_token')


        return response


class RefreshTokenView(TokenRefreshView):
    """
    API endpoint to refresh the JWT access token using the refresh token.

    Permissions:
        - Requires valid refresh token in cookies and Authorization header.

    Behavior:
        - POST:
            - Compares refresh token from cookies and Authorization header.
            - If valid, generates a new access token.
            - Stores the new access token in an HTTP-only cookie.
            - Returns 401 if tokens are missing or do not match.
    """

    def post(self, request, *args, **kwargs):
            token = request.headers.get("Authorization")
            refresh_token = request.COOKIES.get("refresh_token")

            if token is None:
                     return Response({"detail": "RefreshToken invalid"}, status=status.HTTP_401_UNAUTHORIZED)
            
            if token.startswith("Bearer ") :
                    refresh_token_From_headers = token[7:]
            
            
            if refresh_token_From_headers !=  refresh_token:
                return Response({"detail": "RefreshToken invalid"}, status=status.HTTP_401_UNAUTHORIZED)

            seralizer = self.get_serializer(data={"refresh": refresh_token })

            if seralizer.is_valid():
                access_token = seralizer.validated_data.get("access")
                response = Response({'detail': "Token refreshed",  "access": access_token})
                response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="Lax")
        
                return response