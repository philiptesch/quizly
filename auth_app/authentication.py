from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import generics, status

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom authentication class that reads JWT tokens from HttpOnly cookies.

    Purpose:
        - Allows authentication without using the Authorization header.
        - Designed for cookie-based login systems.

    Behavior:
        - Extracts the access token from request cookies.
        - Validates the token and identifies the associated user.
        - Authenticates the request if the token is valid.
    """
    def authenticate(self, request):
        """
        Attempt to authenticate the user using a JWT stored in cookies.

        Process Steps:
        1. Retrieve the 'access_token' from the request cookies.
        2. Validate the token (check signature, expiration, etc.).
        3. Extract the user associated with the validated token.
        4. Return a tuple of (user, validated_token) if authentication succeeds.
        5. Return None if the token is missing, invalid, or expired.
        """
        access_token = request.COOKIES.get("access_token")

        try:
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except Exception:
            return None