from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404

from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    ConversationSerializer,
    MessageSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework import exceptions
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter
from .pagination import MessagePagination


# --------------------
# Conversation ViewSet
# --------------------


class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        # Only return conversations where the user is a participant
        user = self.request.user
        if user.is_authenticated:
            return (
                Conversation.objects.filter(participants=user)
                .prefetch_related("participants", "messages")
            )
        return Conversation.objects.none()
    serializer_class = ConversationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["participants__email"]

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation with participants.
        Expected JSON:
        {
            "participants": [
                "user_id1",
                "user_id2",
                ...
            ]
        }
        """
        participant_ids = request.data.get("participants", [])
        if len(participant_ids) < 2:
            return Response(
                {"error": "A conversation must have atleast 2 participants."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        participants = User.objects.filter(user_id__in=participant_ids)
        if participants.count() != len(participant_ids):
            return Response(
                {"error": "One or more participants do not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ---------------------
# Message ViewSet
# ---------------------


class MessageViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filterset_class = MessageFilter
    pagination_class = MessagePagination

    def handle_exception(self, exc):
        if isinstance(exc, exceptions.PermissionDenied):
            return Response(
                {"detail": "Forbidden"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().handle_exception(exc)

    def get_queryset(self):
        # Only return messages in conversations the user participates in
        user = self.request.user
        if user.is_authenticated:
            return (
                Message.objects.filter(conversation__participants=user)
                .select_related("sender", "conversation")
            )
        return Message.objects.none()
    serializer_class = MessageSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["message_body"]

    def create(self, request, *args, **kwargs):
        """
        Send a new message in a conversation.
        Expected JSON:
        {
            "conversation": "conversation_id",
            "message_body": "",
            "sender": "user_id"
        }
        """
        conversation_id = request.data.get.get("conversation")
        sender_id = request.data.get("sender")
        message_body = request.data.get("message_body")

        if not conversation_id or not sender_id or not message_body:
            return Response(
                {
                    "error": (
                        "conversation, sender, and message_body are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        message = Message.objects.create(
            conversation_id=conversation_id,
            sender_id=sender_id,
            message_body=message_body,
        )
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
