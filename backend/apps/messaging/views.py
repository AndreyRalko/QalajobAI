"""
Messaging Views — Private chat between students and employers.
"""

import logging

from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

logger = logging.getLogger('apps')


class ConversationListView(APIView):
    """List user's conversations or start a new one."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = Conversation.objects.filter(
            participants=request.user
        ).prefetch_related('participants', 'messages')

        serializer = ConversationSerializer(
            conversations, many=True, context={'request': request}
        )
        return Response(serializer.data)

    def post(self, request):
        """Start a new conversation."""
        recipient_id = request.data.get('recipient_id')
        message_text = request.data.get('message', '')

        if not recipient_id:
            return Response(
                {'message': 'recipient_id is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response(
                {'message': 'User not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if recipient == request.user:
            return Response(
                {'message': 'Cannot message yourself'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if conversation already exists
        existing = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=recipient
        ).first()

        if existing:
            conversation = existing
        else:
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, recipient)

        # Send first message if provided
        if message_text:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=message_text,
            )
            conversation.save()  # Update updated_at

        serializer = ConversationSerializer(
            conversation, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageListView(APIView):
    """List messages in a conversation or send a new message."""
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                participants=request.user,
            )
        except Conversation.DoesNotExist:
            return Response(
                {'message': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Mark messages as read
        conversation.messages.filter(is_read=False).exclude(
            sender=request.user
        ).update(is_read=True)

        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                participants=request.user,
            )
        except Conversation.DoesNotExist:
            return Response(
                {'message': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        content = request.data.get('content', '')
        if not content:
            return Response(
                {'message': 'Message content is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content,
        )
        conversation.save()  # Update updated_at

        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UnreadCountView(APIView):
    """Get total unread message count."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False,
        ).exclude(sender=request.user).count()

        return Response({'count': count})
