from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractUser

class UserRole(models.TextChoices):
    GUEST = 'guest'
    HOST = 'host'
    ADMIN = 'admin'

class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    first_name = models.CharField(max_length=30, null=False)
    last_name = models.CharField(max_length=30, null=False)
    email = models.EmailField(unique=True, null=False, db_index=True)
    password_hash = models.CharField(max_length=128, null=False)
    phone_number = models.CharField(max_length=12, null=True)
    role = models.CharField(max_length=10, choices=UserRole.choices, null=False, default=UserRole.GUEST)
    created_at = models.DateTimeField(auto_now_add=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='chats_users_set', # Unique name for this relationship
        related_query_name='chats_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='chats_users_permissions_set', # Unique name for this relationship
        related_query_name='chats_user',
    )

    def __str__(self):
        return self.username

class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE)
    message_body = models.TextField(null=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.sender_id} at {self.sent_at}'

class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    participants_id = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Conversation {self.conversation_id} created at {self.created_at}'
