from rest_framework import serializers
from .models import Resume


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['content', 'file_url', 'ai_analysis', 'ai_score', 'updated_at']
        read_only_fields = ['ai_analysis', 'ai_score', 'updated_at']
