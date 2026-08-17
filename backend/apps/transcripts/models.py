from django.db import models


class TranscriptQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted=0)


class Transcript(models.Model):
    """LMS transcript row (`select * from transcript t where StudentID = ...`)."""

    lms_id = models.BigIntegerField(unique=True, db_index=True)
    student_id = models.CharField(max_length=64, db_index=True)

    subject_code = models.CharField(max_length=64)
    credits = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    alpha_mark = models.CharField(max_length=8, blank=True)
    numeral_mark = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    total_mark = models.DecimalField(max_digits=16, decimal_places=10, null=True, blank=True)

    subject_name_ru = models.CharField(max_length=255, blank=True)
    subject_name_kz = models.CharField(max_length=255, blank=True)
    subject_name_en = models.CharField(max_length=255, blank=True)

    accepted = models.IntegerField(default=0)
    exam_mark = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    retake = models.IntegerField(default=0)
    course_number = models.IntegerField(null=True, blank=True)
    term = models.IntegerField(null=True, blank=True)
    type = models.IntegerField(default=0)
    hash = models.CharField(max_length=128, blank=True)
    mark_id = models.BigIntegerField(null=True, blank=True)
    is_passed = models.BooleanField(null=True, blank=True)

    r1 = models.CharField(max_length=32, blank=True)
    r2 = models.CharField(max_length=32, blank=True)
    pcp = models.CharField(max_length=32, blank=True)

    code_en = models.CharField(max_length=64, blank=True)
    code_ru = models.CharField(max_length=64, blank=True)
    ignore_marks = models.IntegerField(default=0)
    query_id = models.BigIntegerField(null=True, blank=True)
    deleted = models.IntegerField(default=0)

    rewritable_subject_name_kz = models.CharField(max_length=255, blank=True)
    rewritable_subject_name_ru = models.CharField(max_length=255, blank=True)
    rewritable_subject_name_en = models.CharField(max_length=255, blank=True)
    is_transfer_credit = models.IntegerField(default=0)
    modified = models.DateTimeField(null=True, blank=True)
    continuance_subject_id = models.BigIntegerField(null=True, blank=True)
    subject_id = models.BigIntegerField(null=True, blank=True)
    rewritable_subject_code = models.CharField(max_length=64, blank=True)
    is_general_exam = models.IntegerField(default=0)
    ects = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    group_type_id = models.IntegerField(null=True, blank=True)
    subject_study_language = models.IntegerField(null=True, blank=True)

    is_additional_subject = models.IntegerField(default=0)
    is_subject_with_additional_type = models.IntegerField(default=0)
    is_course_work = models.IntegerField(default=0)
    traditional_mark = models.IntegerField(null=True, blank=True)
    calc_as_old_mark = models.IntegerField(default=0)
    created = models.DateTimeField(null=True, blank=True)
    subject_type = models.IntegerField(null=True, blank=True)
    tup_subject_id = models.BigIntegerField(null=True, blank=True)
    old_query_id = models.BigIntegerField(null=True, blank=True)

    academic_difference_course = models.IntegerField(default=0)
    academic_difference_term = models.IntegerField(default=0)
    not_included_scholarship = models.IntegerField(default=0)
    was_retaken = models.IntegerField(default=0)
    re_exam_count = models.IntegerField(default=0)
    re_exam_reason_types = models.CharField(max_length=255, blank=True)
    previous_type = models.IntegerField(null=True, blank=True)
    general_exam_tup_subject_id = models.BigIntegerField(null=True, blank=True)
    degree_id = models.IntegerField(default=0)

    objects = TranscriptQuerySet.as_manager()

    class Meta:
        db_table = "transcript"
        ordering = ["course_number", "term", "subject_code"]
        indexes = [
            models.Index(fields=["student_id", "course_number", "term"]),
            models.Index(fields=["subject_code"]),
        ]

    def __str__(self):
        return f"{self.student_id} {self.subject_code} {self.alpha_mark}".strip()
