from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from chats.views import ConversationViewSet, MessageViewSet, UserViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'conversations', ConversationViewSet,
                basename='conversation')
conversation_routers = nested_routers.NestedDefaultRouter(router, r'conversations',
                                                          lookup='conversation')
conversation_routers.register(r'messages', MessageViewSet,
                              basename='conversation-message')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversation_routers.urls)),
]
