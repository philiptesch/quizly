from rest_framework.permissions import BasePermission



class isOwnerFromTheQuiz(BasePermission):
    """
    Custom permission to allow access only to the owner of a quiz.

    Permissions:
        - User must be authenticated.
        - User must be the owner of the quiz object.

    Behavior:
        - General permission check ensures the user is logged in.
        - Object-level permission allows access only if the quiz.user
          matches the current request.user.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
