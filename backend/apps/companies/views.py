from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsEmployer
from .models import Company
from .serializers import CompanySerializer


class CompanyMeView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def get(self, request):
        try:
            company = request.user.company
        except Company.DoesNotExist:
            return Response({'data': None})
        return Response({'data': CompanySerializer(company).data})

    def put(self, request):
        company, _ = Company.objects.get_or_create(
            owner=request.user,
            defaults={'company_name': request.data.get('company_name', 'My Company')},
        )
        serializer = CompanySerializer(company, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'data': serializer.data})
