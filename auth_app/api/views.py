from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics, status
from .seralizers import RegistrationSerializer, LoginSeralizer
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

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