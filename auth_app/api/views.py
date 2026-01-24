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

    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "User created successfully!"}, status=status.HTTP_201_CREATED)
        
        else: 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginCookieView(TokenObtainPairView):
    serializer_class = LoginSeralizer

    def post(self, request, *args, **kwargs):
        seralizer = self.get_serializer(data=request.data)
        if not seralizer.is_valid():
            return Response(seralizer.errors, status=status.HTTP_401_UNAUTHORIZED)
        refresh = seralizer.validated_data['refresh']
        access = seralizer.validated_data['access']
        response = Response({"detail": "Login successfully!","user": {'id': seralizer.user.id,'username': seralizer.user.username,'email': seralizer.user.email}
    },
    status=status.HTTP_200_OK
)

        response.set_cookie(
            key="access_token", value=access, httponly=True, secure=True, samesite="Lax")
        
        response.set_cookie(
            key="refresh_token", value=refresh, httponly=True, secure=True, samesite="Lax")
        return response
    

class LogoutView(APIView):
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