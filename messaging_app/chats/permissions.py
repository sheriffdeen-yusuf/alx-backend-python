
from rest_framework import permissions


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allows access only to authenticated users who are participants
    in the conversation.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Safe methods (GET, HEAD, OPTIONS) are allowed for participants
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, 'participants'):
                return user in obj.participants.all()
            if hasattr(obj, 'conversation'):
                return user in obj.conversation.participants.all()
            return False
        # PUT, PATCH, DELETE are only allowed for participants
        if request.method in ["PUT", "PATCH", "DELETE"]:
            if hasattr(obj, 'participants'):
                return user in obj.participants.all()
            if hasattr(obj, 'conversation'):
                return user in obj.conversation.participants.all()
            return False
        # POST is allowed for authenticated users (handled by has_permission)
        return True
