from rest_framework import serializers
from .models import User, Message, Conversation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        password = serializers.CharField(write_only=True)
        fields = ['user_id', 'first_name',
                  'last_name', 'email',
                  'phone_number', 'role']
        read_only_fields = ['user_id', 'created_at']
        
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(source='sender_id', read_only=True)
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sent_at']

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True, source='participants_id')
    messages = MessageSerializer(many=True, read_only=True)
    total_messages = serializers.SerializerMethodField()
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']
    
    def get_total_messages(self, obj):
        return obj.messages.count()
    
    def validate(self, data):
        """
        Custom validation to ensure that a user cannot create a conversation with themselves.
        """
        request = self.context.get('request')
        if request and request.user in data.get('participants_id', []):
            raise serializers.ValidationError("You cannot create a conversation with yourself.")
        return data


