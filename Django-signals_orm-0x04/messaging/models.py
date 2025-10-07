from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from .managers import UnreadMessagesManager

# Create your models here.

class User(AbstractUser):
    # extension of the Abstract user for values not defined in the built-in Django User model
    user_id = models.AutoField(primary_key=True, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, blank=False)
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'role', 'password']
    username = models.CharField(max_length=150, unique=True, blank=False)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    password = models.CharField(max_length=128, blank=False)
    phone_number = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(default=models.functions.Now())


class Conversation(models.Model):
    # tracks which users are involved in a conversation
    conversation_id = models.AutoField(primary_key=True, unique=True)
    participants = models.ManyToManyField(User, related_name='conversations')
    creator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_conversations',
        null=True,  
        blank=True 
    )
    created_at = models.DateTimeField(default=models.functions.Now())
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        participant_names = [user.username for user in self.participants.all()]
        return f"Conversation between {', '.join(participant_names)}"

class Message(models.Model):
    # containing the sender, conversation as defined in the shared schema 
    message_id = models.AutoField(primary_key=True, unique=True)
    conversation_id = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    content = models.TextField()
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='edited_messages')
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_thread_starter = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=models.functions.Now())

    class Meta:
        ordering = ['-timestamp']
    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"
    
    def save(self, *args, **kwargs):
        if self.parent_message:
            self.is_thread_starter = False
        else:
            self.is_thread_starter = True
        super().save(*args, **kwargs)

    objects = models.Manager()  # The default manager.
    unread = UnreadMessagesManager()  # Custom manager for unread messages.
    
class MessageHistory(models.Model):
    # to keep track of message edits
    history_id = models.AutoField(primary_key=True, unique=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    edited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-edited_at']

    def __str__(self):
        return f"History of message {self.message.message_id} edited at {self.edited_at}"
    
class Notification(models.Model):
    # to store notifications, linking it to the User and Message models
    NOTIFICATION_TYPES = [
        ('message', 'Message'),
        ('mention', 'Mention'),
        ('other', 'Other'),
    ]
    notification_id = models.AutoField(primary_key=True, unique=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='message')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=models.functions.Now())

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username} about message {self.message.message_id}"