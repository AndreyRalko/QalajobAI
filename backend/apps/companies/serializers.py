from rest_framework import serializers
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    completion = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'owner_id', 'company_name', 'industry', 'location',
            'website', 'company_size', 'description', 'logo',
            'is_verified', 'completion', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'owner_id', 'is_verified', 'created_at', 'updated_at']

    def get_completion(self, obj):
        return obj.completion_percent()
