from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Resume
from .serializers import ResumeSerializer


class ResumeMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        resume, _ = Resume.objects.get_or_create(user=request.user)
        return Response({'data': ResumeSerializer(resume).data})

    def put(self, request):
        resume, _ = Resume.objects.get_or_create(user=request.user)
        serializer = ResumeSerializer(resume, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'data': serializer.data})
