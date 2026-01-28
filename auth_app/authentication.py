from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import generics, status

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads the token from an HttpOnly cookie
    instead of the standard Authorization header.

    Permissions:
        - Used in views that require user authentication.
    
    Behavior:
        - authenticate(request):
            - Looks for an 'access_token' cookie in the incoming request.
            - Validates the token (signature, expiration, etc.).
            - Retrieves the corresponding user from the database.
            - Returns a tuple (user, validated_token) if valid.
            - Returns None if the cookie is missing, invalid, or expired.
    """
    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")

        try:
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except Exception:
            return None