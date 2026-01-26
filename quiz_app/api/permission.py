from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS



class isOwnerFromTheQuiz(BasePermission):
 
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
