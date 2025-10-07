from rest_framework import serializers
from .models import User, Conversation, Message

# --------------------------
# User Serializer
# --------------------------


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            "user_id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "created_at",
            "full_name",
        ]

# --------------------------
# Message Serializer
# --------------------------


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            "message_id",
            "conversation",
            "sender",
            "message_body",
            "sent_at",
        ]
        extra_kwargs = {
            "conversation": {"write_only": True},
        }

# --------------------------
# Conversation Serializer
# --------------------------


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "created_at",
            "messages",
        ]

    def get_messages(self, obj):
        """
        Return message for this conversation using nested MessageSerializer.
        """
        messages = obj.messages.all().order_by("sent_at")
        return MessageSerializer(messages, many=True).data

    def validate(self, data):
        """
        Example custom validation: conversations
        must have atleast 2 participants.
        """
        participants = data.get("participants", [])
        if len(participants) < 2:
            raise serializers.ValidationError(
                "A conversation must have atleast 2 participants."
            )
        return data
