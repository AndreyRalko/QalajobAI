from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsStudent
from apps.vacancies.models import Vacancy

from .models import SavedHhVacancy, SavedJob
from .serializers import (
    SavedHhVacancyCreateSerializer,
    SavedHhVacancySerializer,
    SavedJobSerializer,
)


class SavedJobViewSet(viewsets.ModelViewSet):
    serializer_class = SavedJobSerializer
    permission_classes = [IsAuthenticated, IsStudent]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user).select_related("vacancy")

    def create(self, request, *args, **kwargs):
        vacancy_id = request.data.get("vacancy_id") or request.data.get("vacancyId")
        if not vacancy_id:
            return Response(
                {"message": "vacancy_id required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        vacancy = Vacancy.objects.filter(pk=vacancy_id).first()
        if not vacancy:
            return Response(
                {"message": "Vacancy not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        saved, created = SavedJob.objects.get_or_create(
            user=request.user, vacancy=vacancy
        )
        return Response(
            {"data": SavedJobSerializer(saved).data},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class SavedHhVacancyViewSet(viewsets.ModelViewSet):
    """Save HH vacancies and pick one as active AI context."""

    permission_classes = [IsAuthenticated, IsStudent]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        return SavedHhVacancy.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return SavedHhVacancyCreateSerializer
        return SavedHhVacancySerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return Response({"data": SavedHhVacancySerializer(qs, many=True).data})

    def create(self, request, *args, **kwargs):
        ser = SavedHhVacancyCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        obj, created = SavedHhVacancy.objects.update_or_create(
            user=request.user,
            hh_id=data["hh_id"],
            defaults={
                "title": data["title"],
                "company": data["company"],
                "city": data["city"],
                "salary": data["salary"],
                "url": data["url"],
                "description": data["description"],
            },
        )
        if data.get("select"):
            obj.select_for_user()
        return Response(
            {"data": SavedHhVacancySerializer(obj).data},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="selected")
    def selected(self, request):
        obj = (
            self.get_queryset()
            .filter(is_selected=True)
            .first()
        )
        if not obj:
            return Response({"data": None})
        return Response({"data": SavedHhVacancySerializer(obj).data})

    @action(detail=True, methods=["post"], url_path="select")
    def select(self, request, pk=None):
        obj = self.get_object()
        obj.select_for_user()
        return Response({"data": SavedHhVacancySerializer(obj).data})

    @action(detail=False, methods=["post"], url_path="clear-selected")
    def clear_selected(self, request):
        self.get_queryset().filter(is_selected=True).update(is_selected=False)
        return Response({"data": {"ok": True}})
