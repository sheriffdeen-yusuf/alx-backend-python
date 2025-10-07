from rest_framework import serializers
from .models import User, Conversation, Message, Notification, MessageHistory

# Serializers for the User, Conversation, and Message models

class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='id')
    is_online = serializers.BooleanField(default=False)
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'created_at', 'is_online']
        read_only_fields = ['user_id', 'created_at']

class ConversationSerializer(serializers.ModelSerializer):
    # Nested serializer to include creator details
    creator = UserSerializer(read_only=True)
    # Nested serializer to include participant details
    participants = UserSerializer(many=True, read_only=True)
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.CharField(source='last_message_body', allow_blank=True, default='')

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants_id', 'created_at', 'creator', 'participants', 'unread_count', 'last_message']

    # Method to calculate unread message count for the conversation
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
             return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0
    # Nested representation to validate errors in the participants
    def validate_participants(self, value):
        if not value:
            raise serializers.ValidationError("A conversation must have at least one participant.")
        return value

class MessageSerializer(serializers.ModelSerializer):
    # Nested serializer to include sender and message details
    sender = UserSerializer(read_only=True)
    conversation = ConversationSerializer(read_only=True)
    message = serializers.CharField(source='message_body')

    class Meta:
        model = Message
        fields = ['message_id', 'conversation_id', 'sender_id', 'message', 'sent_at', 'sender', 'conversation']

    # Nested representation to validate errors in the message body
    def validate_message(self, value):
        if not value:
            raise serializers.ValidationError("Message body cannot be empty.")
        return value
    
class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    message = serializers.CharField(source='message_body')

    class Meta:
        model = Notification
        fields = ['notification_id', 'user_id', 'message', 'is_read', 'created_at']

    def validate_message(self, value):
        if not value:
            raise serializers.ValidationError("Notification message cannot be empty.")
        return value
    
class MessageHistorySerializer(serializers.ModelSerializer):
    message = serializers.PrimaryKeyRelatedField(read_only=True)
    edited_by = UserSerializer(read_only=True)

    class Meta:
        model = MessageHistory
        fields = ['history_id', 'message', 'old_content', 'edited_by', 'edited_at']
        read_only_fields = ['history_id', 'message', 'edited_at']