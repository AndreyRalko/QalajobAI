from rest_framework import serializers

from .models import Transcript


class TranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        fields = [
            "id",
            "lms_id",
            "student_id",
            "subject_code",
            "credits",
            "alpha_mark",
            "numeral_mark",
            "total_mark",
            "subject_name_ru",
            "subject_name_kz",
            "subject_name_en",
            "accepted",
            "exam_mark",
            "retake",
            "course_number",
            "term",
            "type",
            "is_passed",
            "code_en",
            "code_ru",
            "is_transfer_credit",
            "modified",
            "subject_id",
            "ects",
            "subject_study_language",
            "traditional_mark",
            "created",
            "subject_type",
            "tup_subject_id",
            "was_retaken",
            "re_exam_count",
            "degree_id",
            "deleted",
        ]
        read_only_fields = fields
