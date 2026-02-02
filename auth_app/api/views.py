
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
from rest_framework_simplejwt.tokens import RefreshToken

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
        """
        Handle POST request to register a new user account.

        Process Steps:
        1. Deserialize and validate incoming registration data using RegistrationSerializer.
        2. If validation succeeds, save the new user to the database.
        3. Return a success response with HTTP 201 status.
        4. If validation fails, return serializer errors with HTTP 400 status.
        """

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
        """
        Handle POST request to authenticate a user and issue JWT tokens via cookies.

        Process Steps:
        1. Validate login credentials using the custom LoginSerializer.
        2. If validation fails, return HTTP 401 with error details.
        3. Extract generated refresh and access tokens from validated data.
        4. Build a success response including basic user information.
        5. Store access and refresh tokens in secure, HTTP-only cookies.
        6. Return the response with HTTP 200 status.
        """
        
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
        """
        Handle POST request to log out the authenticated user.

        Process Steps:
        1. Retrieve access and refresh tokens from cookies.
        2. If no access token is found, return HTTP 400 error.
        3. Blacklist the refresh token so it can no longer be used.
        4. Delete both access and refresh token cookies from the response.
        5. Return a success message confirming logout.
        """

        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")
        if access_token is None:
            return Response({"detail": "access_token not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        response = Response({"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."}, status=status.HTTP_200_OK)

        token = RefreshToken(refresh_token)
        token.blacklist()

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
        """
        Handle POST request to refresh the JWT access token.

        Process Steps:
        1. Retrieve the refresh token from the Authorization header and cookies.
        2. Ensure the Authorization header is present and starts with "Bearer ".
        3. Compare the token from the header with the one stored in cookies.
        4. If tokens do not match, return HTTP 401 Unauthorized.
        5. Validate the refresh token using TokenRefreshView serializer.
        6. Generate a new access token.
        7. Store the new access token in a secure HTTP-only cookie.
        8. Return a success response containing the new access token.
        """    

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