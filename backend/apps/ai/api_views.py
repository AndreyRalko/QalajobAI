"""
QalaJob AI — Additional AI API Views
Career Coach, Employer Assistant, Resume Enhancement, Import, Cover Letter, Interview.
"""

from __future__ import annotations

import io
import logging

from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from apps.resumes.models import Resume

from .models import CareerCoachChat, CoverLetterGeneration, InterviewPrep
from .services.openai_client import (
    adapt_resume_to_vacancy,
    assistant_chat,
    enhance_resume,
    generate_cover_letter_freeform,
    prepare_interview_freeform,
    resume_assistant_chat,
    structure_resume_from_text,
)
from .services.hh_client import (
    extract_vacancy_id,
    get_vacancy,
    search_vacancies,
    vacancy_to_prompt_text,
)

logger = logging.getLogger("apps")

VALID_MODES = frozenset({"resume", "cover_letter", "interview", "mock_interview"})


class AIRateThrottle(UserRateThrottle):
    rate = "100/hour"


def _request_language(request) -> str:
    lang = ""
    if hasattr(request, "data") and request.data is not None:
        try:
            lang = (
                request.data.get("language")
                or request.data.get("locale")
                or ""
            )
        except Exception:
            lang = ""
    if not lang:
        header = request.headers.get("Accept-Language", "")
        if header:
            lang = header.split(",")[0].strip()
    if not lang:
        try:
            profile = request.user.profile
            lang = getattr(profile, "language", None) or "kk"
        except Exception:
            lang = "kk"
    return str(lang).strip() or "kk"


def _normalize_mode(raw) -> str:
    mode = str(raw or "resume").strip().lower()
    if mode in ("interview_prep", "interview-prep"):
        mode = "interview"
    if mode in ("mock", "practice", "rehearsal", "mock-interview"):
        mode = "mock_interview"
    if mode not in VALID_MODES:
        return "resume"
    return mode


def _normalize_messages(messages) -> list:
    out = []
    for msg in messages or []:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role")
        content = msg.get("content")
        if role in ("user", "assistant") and content:
            out.append({"role": role, "content": content})
    return out


def _get_or_create_chat(user, chat_id, topic: str, mode: str) -> CareerCoachChat:
    if chat_id:
        try:
            chat = CareerCoachChat.objects.get(id=chat_id, user=user)
            if chat.mode != mode:
                chat.mode = mode
                chat.save(update_fields=["mode"])
            return chat
        except CareerCoachChat.DoesNotExist:
            pass
    return CareerCoachChat.objects.create(
        user=user,
        topic=(topic or mode)[:100],
        mode=mode,
        messages=[],
    )


def _persist_resume_draft(user, resume_draft: str | None) -> None:
    if resume_draft is None:
        return
    text = str(resume_draft).strip()
    if not text:
        return
    Resume.objects.update_or_create(
        user=user,
        defaults={"content": text},
    )


def _format_interview_document(result: dict) -> str:
    lines: list[str] = []
    questions = result.get("questions") or []
    tips = result.get("tips") or []
    duration = result.get("estimated_duration")
    if duration:
        lines.append(f"Estimated duration: {duration} min")
        lines.append("")
    if questions:
        lines.append("Questions")
        lines.append("---------")
        for i, q in enumerate(questions, 1):
            if isinstance(q, dict):
                lines.append(f"{i}. [{q.get('category', 'general')}] {q.get('question', '')}")
                if q.get("tip"):
                    lines.append(f"   Tip: {q.get('tip')}")
            else:
                lines.append(f"{i}. {q}")
            lines.append("")
    if tips:
        lines.append("Tips")
        lines.append("----")
        for tip in tips:
            lines.append(f"- {tip}")
    return "\n".join(lines).strip()


def _resume_assistant_post(request, error_label: str):
    message = request.data.get("message", "")
    chat_id = request.data.get("chat_id")
    history = request.data.get("history") or []
    resume_draft = request.data.get("resume_draft") or request.data.get("resume") or ""
    # Active document for cover/interview modes (falls back to resume_draft)
    document_draft = (
        request.data.get("document_draft")
        or request.data.get("draft")
        or resume_draft
        or ""
    )
    mode = _normalize_mode(request.data.get("mode"))
    language = _request_language(request)
    # Optional resume context for cover/interview (not written unless mode=resume)
    resume_context = request.data.get("resume_context") or ""
    job_title = (
        request.data.get("job_title")
        or request.data.get("position")
        or ""
    )
    company = request.data.get("company") or ""
    job_description = (
        request.data.get("job_description")
        or request.data.get("description")
        or request.data.get("requirements")
        or ""
    )

    if not message:
        return Response(
            {"message": "Message is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # For a fresh mock interview start, prefer empty history if client sends chat_id=null
        # and an explicit reset flag.
        force_new = bool(request.data.get("new_session") or request.data.get("reset"))
        if force_new and mode == "mock_interview":
            chat_id = None

        topic = message
        if mode == "mock_interview" and job_title:
            topic = f"Mock: {job_title}"[:100]

        chat = _get_or_create_chat(request.user, chat_id, topic, mode)

        stored = _normalize_messages(chat.messages)
        if force_new and mode == "mock_interview":
            history_for_ai = []
            messages = []
        else:
            history_for_ai = stored if stored else _normalize_messages(history)
            messages = list(chat.messages or [])

        messages.append(
            {
                "role": "user",
                "content": message,
                "timestamp": timezone.now().isoformat(),
            }
        )

        draft_for_ai = document_draft
        if force_new and mode == "mock_interview":
            draft_for_ai = ""

        result = resume_assistant_chat(
            message,
            history=history_for_ai,
            language=language,
            resume_draft=draft_for_ai,
            mode=mode,
            resume_context=resume_context if mode != "resume" else "",
            job_title=job_title,
            company=company,
            job_description=job_description,
        )
        reply = result.get("reply") or ""
        new_draft = result.get("document_draft")
        if new_draft is None:
            new_draft = result.get("resume_draft")

        messages.append(
            {
                "role": "assistant",
                "content": reply,
                "timestamp": timezone.now().isoformat(),
            }
        )
        chat.messages = messages
        chat.save(update_fields=["messages", "updated_at", "mode"])

        if mode == "resume":
            _persist_resume_draft(request.user, new_draft)

        return Response(
            {
                "chat_id": chat.id,
                "mode": mode,
                "reply": reply,
                "resume_draft": new_draft if mode == "resume" else None,
                "document_draft": new_draft,
                "messages": _normalize_messages(messages),
            }
        )
    except Exception as e:
        logger.error("%s error: %s", error_label, e)
        return Response(
            {"message": f"Error in {error_label}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _latest_chat_get(request):
    mode = _normalize_mode(request.query_params.get("mode") or "resume")
    chat = (
        CareerCoachChat.objects.filter(user=request.user, mode=mode)
        .order_by("-updated_at")
        .first()
    )
    if not chat:
        return Response({"chat_id": None, "mode": mode, "messages": []})
    return Response(
        {
            "chat_id": chat.id,
            "mode": chat.mode,
            "messages": _normalize_messages(chat.messages),
            "topic": chat.topic,
            "updated_at": chat.updated_at.isoformat(),
        }
    )


class CareerCoachView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AIRateThrottle]

    def get(self, request):
        return _latest_chat_get(request)

    def post(self, request):
        return _resume_assistant_post(request, "career coach")


class ResumeAssistantView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AIRateThrottle]

    def get(self, request):
        return _latest_chat_get(request)

    def post(self, request):
        return _resume_assistant_post(request, "resume assistant")


class AssistantChatView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AIRateThrottle]

    def post(self, request):
        message = request.data.get("message", "")
        history = request.data.get("history") or []
        language = _request_language(request)

        if not message:
            return Response(
                {"message": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reply = assistant_chat(message, history=history, language=language)
            if not reply:
                reply = "I'm temporarily unavailable. Please try again."
            return Response({"reply": reply})
        except Exception as e:
            logger.error("Assistant chat error: %s", e)
            return Response(
                {"message": "Error in AI assistant"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ResumeEnhanceView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AIRateThrottle]

    def post(self, request):
        resume_text = (
            request.data.get("resume")
            or request.data.get("content")
            or ""
        )
        language = _request_language(request)

        if not resume_text:
            return Response(
                {"message": "Resume text is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            enhanced = enhance_resume(resume_text, language=language)
            if not enhanced:
                return Response(
                    {"message": "AI service is temporarily unavailable"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            _persist_resume_draft(request.user, enhanced)
            return Response({"enhancedResume": enhanced})
        except Exception as e:
            logger.error("Resume enhance error: %s", e)
            return Response(
                {"message": "Error enhancing resume"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CoverLetterFreeView(APIView):
    """
    POST /api/v1/ai/cover-letter/
    { job_title, company, job_description?, tone?, resume?, language? }
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [AIRateThrottle]

    def post(self, request):
        job_title = (request.data.get("job_title") or request.data.get("position") or "").strip()
        company = (request.data.get("company") or "").strip()
        job_description = (
            request.data.get("job_description")
            or request.data.get("description")
            or ""
        )
        tone = request.data.get("tone") or "professional"
        language = _request_language(request)

        resume_text = (
            request.data.get("resume")
            or request.data.get("resume_text")
            or ""
        )
        if not resume_text:
            resume, _ = Resume.objects.get_or_create(user=request.user)
            resume_text = resume.content or ""

        if not job_title:
            return Response(
                {"message": "job_title is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = generate_cover_letter_freeform(
                resume_text=resume_text,
                job_title=job_title,
                company=company,
                job_description=job_description,
                tone=tone,
                language=language,
            )
            if not result:
                return Response(
                    {"message": "AI service is temporarily unavailable"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            cover = CoverLetterGeneration.objects.create(
                user=request.user,
                vacancy_id="custom",
                cover_letter=result.get("cover_letter", ""),
                tone=tone,
                company=company or None,
                position=job_title,
                key_points=result.get("key_points", []),
            )
            return Response(
                {
                    "id": cover.id,
                    "cover_letter": result.get("cover_letter", ""),
                    "document_draft": result.get("cover_letter", ""),
                    "key_points": result.get("key_points", []),
                }
            )
        except Exception as e:
            logger.error("Cover letter freeform error: %s", e)
            return Response(
                {"message": "Error generating cover letter"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class InterviewPrepFreeView(APIView):
    """
    POST /api/v1/ai/interview-prep/
    { job_title, company?, requirements?, difficulty?, language? }
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [AIRateThrottle]

    def post(self, request):
        job_title = (request.data.get("job_title") or request.data.get("position") or "").strip()
        company = (request.data.get("company") or "").strip()
        requirements = (
            request.data.get("requirements")
            or request.data.get("job_description")
            or request.data.get("description")
            or ""
        )
        difficulty = request.data.get("difficulty") or "medium"
        language = _request_language(request)

        if not job_title:
            return Response(
                {"message": "job_title is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = prepare_interview_freeform(
                job_title=job_title,
                company=company,
                requirements=requirements,
                difficulty=difficulty,
                language=language,
            )
            if not result:
                return Response(
                    {"message": "AI service is temporarily unavailable"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            prep = InterviewPrep.objects.create(
                user=request.user,
                vacancy_id="custom",
                questions=result.get("questions", []),
                tips=result.get("tips", []),
                estimated_duration=result.get("estimated_duration") or 45,
                difficulty=difficulty,
            )
            document = _format_interview_document(result)
            return Response(
                {
                    "id": prep.id,
                    "questions": result.get("questions", []),
                    "tips": result.get("tips", []),
                    "estimated_duration": result.get("estimated_duration") or 45,
                    "document_draft": document,
                }
            )
        except Exception as e:
            logger.error("Interview prep freeform error: %s", e)
            return Response(
                {"message": "Error generating interview prep"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ImportResumeView(APIView):
    """
    POST /api/v1/ai/import-resume/
    JSON: { text, source?: paste|linkedin, language?, save?: true }
    Multipart: file (pdf) + optional source/language/save
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [AIRateThrottle]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        language = _request_language(request)
        source = (request.data.get("source") or "paste").strip().lower()
        save = str(request.data.get("save", "true")).lower() not in ("0", "false", "no")

        raw_text = (request.data.get("text") or request.data.get("content") or "").strip()

        upload = request.FILES.get("file") or request.FILES.get("pdf")
        if upload and not raw_text:
            name = (upload.name or "").lower()
            if not name.endswith(".pdf"):
                return Response(
                    {"message": "Only PDF files are supported"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                from pypdf import PdfReader

                reader = PdfReader(io.BytesIO(upload.read()))
                pages = []
                for page in reader.pages:
                    pages.append(page.extract_text() or "")
                raw_text = "\n".join(pages).strip()
                source = source if source != "paste" else "pdf"
            except Exception as e:
                logger.error("PDF extract error: %s", e)
                return Response(
                    {"message": "Failed to read PDF"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if not raw_text:
            return Response(
                {"message": "text or PDF file is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = structure_resume_from_text(
                raw_text,
                language=language,
                source=source,
            )
            resume_text = result.get("resume") or raw_text
            if save and resume_text.strip():
                _persist_resume_draft(request.user, resume_text)

            return Response(
                {
                    "resume": resume_text,
                    "document_draft": resume_text,
                    "notes": result.get("notes") or "",
                    "source": source,
                    "saved": bool(save and resume_text.strip()),
                }
            )
        except Exception as e:
            logger.error("Import resume error: %s", e)
            return Response(
                {"message": "Error importing resume"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class HhVacancySearchView(APIView):
    """
    GET /api/v1/ai/hh/vacancies/?text=php&area=40&page=0&per_page=20
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [AIRateThrottle]

    def get(self, request):
        text = request.query_params.get("text") or request.query_params.get("q") or ""
        area = request.query_params.get("area")
        page = request.query_params.get("page") or 0
        per_page = request.query_params.get("per_page") or 20
        try:
            data = search_vacancies(
                text=text,
                area=area,
                page=int(page),
                per_page=int(per_page),
            )
            return Response(data)
        except Exception as e:
            logger.error("HH search error: %s", e)
            return Response(
                {"message": str(e) or "Error searching HeadHunter"},
                status=status.HTTP_502_BAD_GATEWAY,
            )


class HhVacancyDetailView(APIView):
    """
    GET /api/v1/ai/hh/vacancies/<id>/
    Also accepts ?url=https://hh.kz/vacancy/123
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [AIRateThrottle]

    def get(self, request, vacancy_id=None):
        url = request.query_params.get("url") or ""
        vid = vacancy_id or extract_vacancy_id(url) or ""
        if not vid:
            return Response(
                {"message": "vacancy_id or url is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            data = get_vacancy(vid)
            return Response(data)
        except LookupError:
            return Response(
                {"message": "Vacancy not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except PermissionError as e:
            return Response({"message": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error("HH vacancy detail error: %s", e)
            return Response(
                {"message": str(e) or "Error fetching vacancy"},
                status=status.HTTP_502_BAD_GATEWAY,
            )


class HhAdaptResumeView(APIView):
    """
    POST /api/v1/ai/hh/adapt-resume/
    {
      "vacancy_id": "123" | "demo-php-1",
      "url": "https://hh.kz/vacancy/123",  # optional
      "resume": "...",                     # optional, else saved resume
      "save": true,
      "language": "ru"
    }
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [AIRateThrottle]

    def post(self, request):
        language = _request_language(request)
        vacancy_id = request.data.get("vacancy_id") or ""
        url = request.data.get("url") or ""
        save = str(request.data.get("save", "true")).lower() not in ("0", "false", "no")
        resume_text = (
            request.data.get("resume")
            or request.data.get("resume_text")
            or ""
        )

        vid = extract_vacancy_id(str(vacancy_id)) or extract_vacancy_id(url) or str(vacancy_id).strip()
        if not vid:
            return Response(
                {"message": "vacancy_id or url is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not resume_text:
            resume, _ = Resume.objects.get_or_create(user=request.user)
            resume_text = resume.content or ""

        try:
            vacancy = get_vacancy(vid)
            vacancy_text = vacancy_to_prompt_text(vacancy)
            result = adapt_resume_to_vacancy(
                resume_text=resume_text,
                vacancy_text=vacancy_text,
                language=language,
            )
            adapted = result.get("adapted_resume") or ""
            if save and adapted.strip():
                _persist_resume_draft(request.user, adapted)

            return Response(
                {
                    "vacancy": vacancy,
                    "adapted_resume": adapted,
                    "document_draft": adapted,
                    "match_notes": result.get("match_notes") or "",
                    "missing_skills": result.get("missing_skills") or [],
                    "saved": bool(save and adapted.strip()),
                }
            )
        except LookupError:
            return Response(
                {"message": "Vacancy not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except PermissionError as e:
            return Response({"message": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error("HH adapt resume error: %s", e)
            return Response(
                {"message": "Error adapting resume to vacancy"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
