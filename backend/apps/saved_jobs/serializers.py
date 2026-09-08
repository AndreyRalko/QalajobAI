from rest_framework import serializers
from apps.vacancies.serializers import VacancySerializer
from .models import SavedJob, SavedHhVacancy


class SavedJobSerializer(serializers.ModelSerializer):
    vacancy = VacancySerializer(read_only=True)
    vacancy_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = SavedJob
        fields = ["id", "vacancy", "vacancy_id", "saved_at"]
        read_only_fields = ["id", "saved_at"]


class SavedHhVacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedHhVacancy
        fields = [
            "id",
            "hh_id",
            "title",
            "company",
            "city",
            "salary",
            "url",
            "description",
            "is_selected",
            "saved_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_selected", "saved_at", "updated_at"]


class SavedHhVacancyCreateSerializer(serializers.Serializer):
    hh_id = serializers.CharField(max_length=64, required=False, allow_blank=True)
    id = serializers.CharField(max_length=64, required=False, allow_blank=True)
    title = serializers.CharField(max_length=300, required=False, allow_blank=True)
    name = serializers.CharField(max_length=300, required=False, allow_blank=True)
    company = serializers.CharField(max_length=300, required=False, allow_blank=True)
    city = serializers.CharField(max_length=120, required=False, allow_blank=True)
    area = serializers.CharField(max_length=120, required=False, allow_blank=True)
    salary = serializers.CharField(max_length=120, required=False, allow_blank=True)
    url = serializers.CharField(max_length=500, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    requirement = serializers.CharField(required=False, allow_blank=True)
    responsibility = serializers.CharField(required=False, allow_blank=True)
    select = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        hh_id = (attrs.get("hh_id") or attrs.get("id") or "").strip()
        title = (attrs.get("title") or attrs.get("name") or "").strip()
        if not hh_id:
            raise serializers.ValidationError({"hh_id": "hh_id is required"})
        if not title:
            raise serializers.ValidationError({"title": "title is required"})
        attrs["hh_id"] = hh_id
        attrs["title"] = title
        attrs["company"] = (attrs.get("company") or "").strip()
        attrs["city"] = (attrs.get("city") or attrs.get("area") or "").strip()
        attrs["salary"] = (attrs.get("salary") or "").strip()
        attrs["url"] = (attrs.get("url") or "").strip()

        description = (attrs.get("description") or "").strip()
        if not description:
            parts = []
            if attrs["city"]:
                parts.append(f"Город: {attrs['city']}")
            if attrs["salary"]:
                parts.append(f"Зарплата: {attrs['salary']}")
            if attrs.get("requirement"):
                parts.append(f"Требования: {attrs['requirement'].strip()}")
            if attrs.get("responsibility"):
                parts.append(f"Обязанности: {attrs['responsibility'].strip()}")
            if attrs["url"]:
                parts.append(f"Ссылка: {attrs['url']}")
            description = "\n\n".join(parts)
        attrs["description"] = description
        return attrs
