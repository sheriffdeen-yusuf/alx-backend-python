from rest_framework.decorators import action
from rest_framework import viewsets, status
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import User, Conversation, Message, Notification, MessageHistory
from .managers import UnreadMessagesManager
from .pagination import CustomPagination
from .permissions import IsParticipantOfConversation
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer, NotificationSerializer, MessageHistorySerializer


# Filters for searching and ordering
class ConversationFilter(filters.FilterSet):
    participant_username = filters.CharFilter(
        field_name='participants__username', 
        lookup_expr='icontains',
        help_text="Filter by participant username"
    )
    created_after = filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='gt',
        help_text="Filter conversations created after this date"
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='lt',
        help_text="Filter conversations created before this date"
    )

    class Meta:
        model = Conversation
        fields = ['participant_username', 'created_after', 'created_before']


class MessageFilter(filters.FilterSet):
    sender_username = filters.CharFilter(
        field_name='sender__username', 
        lookup_expr='icontains',
        help_text="Filter by sender username"
    )
    sent_after = filters.DateTimeFilter(
        field_name='sent_at', 
        lookup_expr='gt',
        help_text="Filter messages sent after this date"
    )
    sent_before = filters.DateTimeFilter(
        field_name='sent_at', 
        lookup_expr='lt',
        help_text="Filter messages sent before this date"
    )
    unread_only = filters.BooleanFilter(
        field_name='is_read', 
        lookup_expr='isnull',
        help_text="Filter only unread messages"
    )

    class Meta:
        model = Message
        fields = ['sender_username', 'sent_after', 'sent_before', 'unread_only']


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    http_method_names = ['get', 'head', 'options', 'post', 'delete']
    filter_backends = [filters.CharFilter, filters.OrderingFilter]
    search_fields = ['username', 'email']
    ordering_fields = ['username', 'date_joined']
    ordering = ['username']

    # Get serializer class for user
    def get_queryset(self):
        return User.objects.all().only(
                'id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'role'
            )
    
    # Delete user view for deleting user accounts
class UserDeleteViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['delete']
    lookup_field = 'id'
    lookup_value_regex = '[0-9]+'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(id=user.id)

@action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
def delete_user(self, request, pk=None):
    try:
        user = self.get_object()
        user.delete()
        return Response({"message": "User account deleted successfully."}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)
    
@action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
def get_unread_messages(self, request):
    user = request.user
    unread_messages = Message.unread.unread_for_user(user)
    serializer = MessageSerializer(unread_messages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ConversationFilter
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    # Return only conversations where the user is a participant
    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(participants=user)
    
    def perform_create(self, serializer):
        conversation = serializer.save(creator=self.request.user)
        conversation.participants.add(self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_conversation(self, request):
        serializer = ConversationSerializer(data=request.data)
        if serializer.is_valid():
            conversation = serializer.save(creator=request.user)
            conversation.participants.add(request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Send a message in the conversation
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsParticipantOfConversation])
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, conversation_id=conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    http_method_names = ['get', 'post', 'put', 'delete']
    lookup_field = 'message_id'
    lookup_value_regex = '[0-9]+'
    filterset_class = MessageFilter
    pagination_class = CustomPagination
    permission_classes = [IsParticipantOfConversation]
    
    # Return only messages in conversations where the user is a participant
    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(conversation__participants=user)

    def perform_create(self, serializer, request):
        # Ensure the user is a participant of the conversation
        try:
            conversation_id = self.request.data.get('conversation_id')
            conversation = Conversation.objects.get(conversation_id=conversation_id)
            if request.user not in conversation.participants.all():
                return Response({"error": "You are not a participant of this conversation."}, 
                                status=status.HTTP_403_FORBIDDEN)
            serializer.save(sender=request.user, conversation_id=conversation)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation does not exist."}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def send_message(self, request, conversation_id=None):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, conversation_id=conversation_id)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    http_method_names = ['get', 'post']
    lookup_field = 'notification_id'
    lookup_value_regex = '[0-9]+'
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user)

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset)

    # Mark notifications as read for the user
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_all_as_read(self, request):
        user = request.user
        notifications = Notification.objects.filter(user=user, is_read=False)
        notifications.update(is_read=True)
        return Response({"message": f"{notifications.count()} notifications marked as read."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsParticipantOfConversation])
    def user_notification(self, request, pk=None):
        user = self.get_object()
        notifications = Notification.objects.filter(user=user, is_read=False)
        # Mark notifications as read
        notifications.update(is_read=True)
        return Response({"message": f"{notifications.count()} notifications marked as read."}, status=status.HTTP_200_OK)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@method_decorator(cache_page(60*2), name='dispatch')  # Cache for 2 minutes
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    http_method_names = ['get', 'post', 'put', 'delete']
    lookup_field = 'message_id'
    lookup_value_regex = '[0-9]+'
    filterset_class = MessageFilter
    pagination_class = CustomPagination
    permission_classes = [IsParticipantOfConversation]
    
    # Return only messages in conversations where the user is a participant
    def get_queryset(self):
        user = self.request.user
        return Message.objects.select_related('receiver').prefetch_related('replies').filter(sender=self.request.user) | Message.objects.select_related('sender').prefetch_related('replies').filter(receiver=self.request.user)

    def perform_create(self, serializer, request):
        # Ensure the user is a participant of the conversation
        try:
            conversation_id = self.request.data.get('conversation_id')
            conversation = Conversation.objects.get(conversation_id=conversation_id)
            if request.user not in conversation.participants.all():
                return Response({"error": "You are not a participant of this conversation."}, 
                                status=status.HTTP_403_FORBIDDEN)
            serializer.save(sender=request.user, conversation_id=conversation)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation does not exist."}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=400)



class MessageEditHistoryViewSet(viewsets.ModelViewSet):
    queryset = MessageHistory.objects.all()
    serializer_class = MessageHistorySerializer
    http_method_names = ['get', 'post']
    lookup_field = 'history_id'
    lookup_value_regex = '[0-9]+'
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsParticipantOfConversation])
    def edit_message(self, request, message_id=None):
        try:
            message = Message.objects.get(message_id=message_id)
            if request.user != message.sender:
                return Response({"error": "You can only edit your own messages."}, status=403)
            new_content = request.data.get('content')
            if not new_content:
                return Response({"error": "Content cannot be empty."}, status=400)
            # Save old content to history
            MessageHistory.objects.create(
                message=message,
                old_content=message.content,
                edited_by=request.user
            )
            # Update message content
            message.content = new_content
            message.edited = True
            message.edited_by = request.user
            message.save()
            return Response({"message": "Message edited successfully."}, status=200)
        except Message.DoesNotExist:
            return Response({"error": "Message not found."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsParticipantOfConversation])
    def message_history(self, request, message_id=None):
        try:
            message = Message.objects.get(message_id=message_id)
            history = MessageHistory.objects.filter(message=message).order_by('-edited_at')
            serializer = MessageHistorySerializer(history, many=True)
            return Response(serializer.data, status=200)
        except Message.DoesNotExist:
            return Response({"error": "Message not found."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        