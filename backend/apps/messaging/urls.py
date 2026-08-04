from django.urls import path
from .views import ConversationListView, MessageListView, UnreadCountView

app_name = 'messaging'

urlpatterns = [
    path('conversations/', ConversationListView.as_view(), name='conversations'),
    path('conversations/<int:conversation_id>/messages/', MessageListView.as_view(), name='messages'),
    path('unread-count/', UnreadCountView.as_view(), name='unread-count'),
]
