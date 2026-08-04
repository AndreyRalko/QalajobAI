from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_participants', 'updated_at']
    list_filter = ['updated_at']

    def get_participants(self, obj):
        return ', '.join([u.email for u in obj.participants.all()])
    get_participants.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'content_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']

    def content_preview(self, obj):
        return obj.content[:80]
    content_preview.short_description = 'Content'
