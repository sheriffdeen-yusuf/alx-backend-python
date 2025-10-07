import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# --------------------------
# User Model
# --------------------------


class User(AbstractUser):
    """
    Custom user model extending AbstractUser.
    Adds fields not present in the built-in User model.
    """
    user_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    ROLE_CHOICES = [
        ("guest", "Guest"),
        ("host", "Host"),
        ("admin", "Admin"),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="guest"
    )

    password = models.CharField(max_length=128)

    created_at = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    @property
    def id(self):
        return self.user_id

    def __str__(self):
        return f"{self.email} ({self.role})"

# --------------------------
# Coversation Model
# --------------------------


class Conversation(models.Model):
    """
    A conversation involving multiple users.
    Many-to-Many relation since multiple users can belong to multiple
    conversations.
    """
    conversation_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Conversation {self.conversation_id}"

# --------------------------
# Message Model
# --------------------------


class Message(models.Model):
    """
    Messages exchanged in conversations.
    Each message is linked to a single conversation and a single sender.
    """
    message_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages"
    )
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    message_body = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message {self.message_id} from {self.sender.email}"
