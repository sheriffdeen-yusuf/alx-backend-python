from rest_framework import permissions
from .models import Conversation, Message

# Custom permission to allow only if the user is authenticated and is a participant in the conversation
class IsParticipantOfConversation(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow access only to authenticated users
        if not request.user or not request.user.is_authenticated:
            return False
        return True
    def has_object_permission(self, request, view, obj):
        # A user can access the conversation if they are a participant
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()
        # A user can view or modify a message if they are the sender
        if isinstance(obj, Message):
            # A user can view message if they are a participant in the conversation
            if request.method == 'GET':
                return request.user in obj.conversation_id.participants.all()
            # A user can modify message if they are the sender
            if request.method in ['PUT', 'DELETE', 'PATCH']:
                return obj.sender_id == request.user
        return False