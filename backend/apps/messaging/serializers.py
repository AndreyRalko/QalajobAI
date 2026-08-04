from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conversation, Message


class ParticipantSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'role']

    def get_name(self, obj):
        return obj.get_full_name() or obj.email.split('@')[0]

    def get_role(self, obj):
        try:
            return obj.profile.role
        except Exception:
            return 'student'


class MessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source='sender.id', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender_id', 'content', 'is_read', 'created_at']
        read_only_fields = ['id', 'sender_id', 'is_read', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'participant', 'last_message', 'unread_count', 'updated_at']

    def get_participant(self, obj):
        request = self.context.get('request')
        if request:
            other = obj.get_other_participant(request.user)
            if other:
                return ParticipantSerializer(other).data
        return None

    def get_last_message(self, obj):
        msg = obj.last_message
        return msg.content[:100] if msg else None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request:
            return obj.unread_count(request.user)
        return 0
