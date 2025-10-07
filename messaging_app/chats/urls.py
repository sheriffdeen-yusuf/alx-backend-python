from django.urls import path, include
# from rest_framework import routers
from rest_framework_nested import routers
from .views import ConversationViewSet, MessageViewSet

# Base router for conversations
router = routers.DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversations")

# Nested router: messages belong to conversations
conversation_router = routers.NestedDefaultRouter(
    router, r"conversations",
    lookup="conversation"
    )
router.register(r"messages", MessageViewSet, basename="message")

# urlpatterns = [
#     path("", include(router.urls)),
# ]

urlpatterns = router.urls + conversation_router.urls
