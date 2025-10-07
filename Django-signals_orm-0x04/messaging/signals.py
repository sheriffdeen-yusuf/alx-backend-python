from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Message, MessageHistory, Notification
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type='message'
        )
        logger.info(f"Notification created for user {instance.receiver.username} about message {instance.message_id}")

@receiver(post_save, sender=Message)
def handle_new_messages(sender, instance, created, **kwargs):
    if created:
        # If the message is a reply, ensure the parent message is marked as not a thread starter
        if instance.parent_message:
            instance.parent_message.is_thread_starter = False
            instance.parent_message.save(update_fields=['is_thread_starter'])
            logger.info(f"Message {instance.parent_message.message_id} marked as not a thread starter due to reply.")
        else:
            instance.is_thread_starter = True
            instance.save(update_fields=['is_thread_starter'])
            logger.info(f"Message {instance.message_id} is a thread starter.")

# Log the old content of a message into a separate MessageHistory model before it’s updated.
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.pk:
        old_message = Message.objects.get(pk=instance.pk)
        if old_message.content != instance.content:
            history = MessageHistory.objects.create(
                message=old_message,
                old_content=old_message.content
            )
            # Update message edited fields
            Message.objects.filter(pk=instance.pk).update(edited=True, edited_by=instance.sender)
            instance.edited = True
            instance.edited_by = instance.sender
            logger.info(f"Message {instance.message_id} edited. Old content logged.")

# delete user and all related messages and conversations
@receiver(post_delete, sender=Message)
def log_message_deletion(sender, instance, **kwargs):
    logger.info(f"Message {instance.message_id} deleted.")
def delete_user_related_data(user):
    messages_deleted, _ = Message.objects.filter(sender=user).delete()
    conversations_deleted, _ = user.created_conversations.all().delete()
    notifications_deleted, _ = Notification.objects.filter(user=user).delete()
    logger.info(f"Deleted {messages_deleted} messages, {conversations_deleted} conversations, and {notifications_deleted} notifications for user {user.username}")