from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser

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
    timestamp = models.DateTimeField(default=models.functions.Now())

    class Meta:
        ordering = ['-timestamp']
    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"