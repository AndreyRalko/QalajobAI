from decimal import Decimal

from django.db.models import Count, Sum
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transcript
from .serializers import TranscriptSerializer


def _student_id(user):
    profile = getattr(user, "profile", None)
    return getattr(profile, "student_id", None) if profile else None


@extend_schema(tags=["Transcript"])
class TranscriptListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student_id = _student_id(request.user)
        if not student_id:
            return Response({"data": []})

        rows = Transcript.objects.active().filter(student_id=student_id)
        return Response({"data": TranscriptSerializer(rows, many=True).data})


@extend_schema(tags=["Transcript"])
class TranscriptSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student_id = _student_id(request.user)
        if not student_id:
            return Response({"data": {"student_id": None, "subjects": 0}})

        rows = Transcript.objects.active().filter(student_id=student_id)
        graded = rows.exclude(alpha_mark="").exclude(alpha_mark__isnull=True)
        totals = graded.aggregate(
            subjects=Count("id"),
            credits=Sum("credits"),
        )
        subject_count = totals["subjects"] or 0
        credit_sum = totals["credits"]
        gpa = None
        if credit_sum:
            weighted = sum(
                (row.numeral_mark or Decimal("0")) * (row.credits or Decimal("0"))
                for row in graded
            )
            gpa = weighted / credit_sum

        return Response(
            {
                "data": {
                    "student_id": student_id,
                    "subjects": rows.count(),
                    "graded_subjects": subject_count,
                    "credits": credit_sum,
                    "gpa": gpa,
                }
            }
        )
