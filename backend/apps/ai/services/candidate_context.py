from decimal import Decimal

from django.db.models import Count, Sum

from apps.transcripts.models import Transcript


def _transcript_summary(student_id: str | None) -> dict:
    if not student_id:
        return {
            "student_id": None,
            "subjects_count": 0,
            "graded_subjects": 0,
            "credits": None,
            "gpa": None,
            "subjects": [],
        }

    rows = Transcript.objects.active().filter(student_id=student_id)
    graded = rows.exclude(alpha_mark="").exclude(alpha_mark__isnull=True)
    totals = graded.aggregate(subjects=Count("id"), credits=Sum("credits"))
    credit_sum = totals["credits"]
    gpa = None
    if credit_sum:
        weighted = sum(
            (row.numeral_mark or Decimal("0")) * (row.credits or Decimal("0"))
            for row in graded
        )
        gpa = weighted / credit_sum

    subjects = []
    for row in rows.order_by("course_number", "term", "subject_code"):
        name = row.subject_name_ru or row.subject_name_en or row.subject_name_kz
        subjects.append(
            {
                "code": row.subject_code,
                "name": name,
                "grade": row.alpha_mark or str(row.numeral_mark or ""),
                "credits": str(row.credits) if row.credits is not None else "",
                "passed": bool(row.is_passed),
                "course": row.course_number,
                "term": row.term,
            }
        )

    return {
        "student_id": student_id,
        "subjects_count": rows.count(),
        "graded_subjects": totals["subjects"] or 0,
        "credits": credit_sum,
        "gpa": float(gpa) if gpa is not None else None,
        "subjects": subjects,
    }


def build_candidate_context(user, job_interests: str = "") -> dict:
    user_profile = getattr(user, "profile", None)
    student_id = getattr(user_profile, "student_id", None) if user_profile else None
    transcript = _transcript_summary(student_id)

    passed_subjects = [s for s in transcript["subjects"] if s["passed"] and s["grade"]]
    if not passed_subjects:
        passed_subjects = [s for s in transcript["subjects"] if s["name"]]

    return {
        "job_interests": job_interests.strip(),
        "transcript_summary": {
            "student_id": transcript["student_id"],
            "subjects_count": transcript["subjects_count"],
            "graded_subjects": transcript["graded_subjects"],
            "credits": str(transcript["credits"]) if transcript["credits"] is not None else None,
            "gpa": transcript["gpa"],
        },
        "transcript_subjects": passed_subjects[:40],
    }


def format_transcript_for_prompt(candidate: dict) -> str:
    summary = candidate["transcript_summary"]
    lines = [
        f"GPA: {summary.get('gpa') if summary.get('gpa') is not None else 'N/A'}",
        f"Subjects: {summary.get('subjects_count', 0)}",
    ]
    for subject in candidate.get("transcript_subjects", [])[:30]:
        grade = subject.get("grade") or "-"
        lines.append(
            f"- {subject.get('code', '')} {subject.get('name', '')} "
            f"(grade: {grade}, course {subject.get('course')}, term {subject.get('term')})"
        )
    return "\n".join(lines)
