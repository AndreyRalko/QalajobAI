"""
OpenAI client for QalaJob AI.
Uses the Chat Completions HTTP API via requests (avoids openai/httpx SDK conflicts).
"""

from __future__ import annotations

import json
import logging
import time
from typing import Optional

import requests
from django.conf import settings

from .action_log import log_openai_exchange
from .prompt_guard import (
    format_history_for_prompt,
    hardened_system,
    sanitize_client_history,
    sanitize_document_draft,
    sanitize_reply_text,
    wrap_untrusted,
)

logger = logging.getLogger("apps")

DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"


class OpenAIClient:
    """Thin wrapper around an OpenAI-compatible Chat Completions API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        provider: str = "openai",
        require_api_key: bool = True,
    ):
        raw_key = api_key if api_key is not None else getattr(settings, "OPENAI_API_KEY", "")
        self.api_key = str(raw_key or "").strip().strip('"').strip("'")
        self.model = model or getattr(settings, "OPENAI_MODEL", "gpt-4o-mini") or "gpt-4o-mini"
        self.base_url = (base_url or DEFAULT_OPENAI_BASE_URL).rstrip("/")
        self.chat_url = f"{self.base_url}/chat/completions"
        self.timeout = timeout or getattr(settings, "LLM_OPENAI_TIMEOUT", 60)
        self.provider = provider or "openai"
        self.require_api_key = require_api_key

    def _call(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        *,
        log_provider: str | None = None,
    ) -> str:
        started = time.perf_counter()
        provider_label = log_provider or self.provider

        if self.require_api_key and not self.api_key:
            logger.warning("OpenAI API key not configured — demo response")
            last_user = next(
                (m.get("content", "") for m in reversed(messages) if m.get("role") == "user"),
                "",
            )
            response_text = (
                "[Demo mode] Configure OPENAI_API_KEY or LLM_OPENAI_API_KEY in backend/.env for live AI. "
                f"You asked: {str(last_user)[:200]}"
            )
            log_openai_exchange(
                messages=messages,
                response_text=response_text,
                model_name=self.model,
                duration_ms=int((time.perf_counter() - started) * 1000),
                status="demo",
                provider=provider_label,
            )
            return response_text

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = requests.post(
                self.chat_url,
                headers=headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=self.timeout,
            )
            duration_ms = int((time.perf_counter() - started) * 1000)
            if response.status_code >= 400:
                error_text = response.text[:500]
                logger.error(
                    "LLM API error (%s) %s: %s",
                    provider_label,
                    response.status_code,
                    error_text,
                )
                log_openai_exchange(
                    messages=messages,
                    response_text="",
                    model_name=self.model,
                    duration_ms=duration_ms,
                    status="failed",
                    error_message=f"HTTP {response.status_code}: {error_text}",
                    provider=provider_label,
                )
                return ""

            data = response.json()
            response_text = (data["choices"][0]["message"]["content"] or "").strip()
            log_openai_exchange(
                messages=messages,
                response_text=response_text,
                model_name=self.model,
                duration_ms=duration_ms,
                status="success" if response_text else "failed",
                error_message="" if response_text else "Empty AI response",
                provider=provider_label,
            )
            return response_text
        except Exception as exc:
            duration_ms = int((time.perf_counter() - started) * 1000)
            logger.error("LLM API error (%s): %s", provider_label, exc)
            log_openai_exchange(
                messages=messages,
                response_text="",
                model_name=self.model,
                duration_ms=duration_ms,
                status="failed",
                error_message=str(exc),
                provider=provider_label,
            )
            return ""

    def _call_json(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> dict:
        messages = [dict(m) for m in messages]
        messages[-1]["content"] += "\n\nRespond ONLY with valid JSON. No markdown, no code blocks."
        raw = self._call(messages, temperature, max_tokens)
        if not raw:
            return {}

        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [line for line in lines if not line.strip().startswith("```")]
            cleaned = "\n".join(lines)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from AI response: %s", raw[:200])
            return {}


# ── Prompt Templates ────────────────────────────────────────────────

RESUME_ANALYSIS_PROMPT = """You are an expert HR analyst and career coach. Analyze the following resume text and provide a detailed assessment.

Resume:
{resume_text}

Target Role (if any): {target_role}

Provide your analysis as JSON with these fields:
{{
  "overall_score": <integer 0-100>,
  "strengths": ["strength1", "strength2", ...],
  "weaknesses": ["weakness1", "weakness2", ...],
  "suggestions": ["suggestion1", "suggestion2", ...],
  "key_skills": ["skill1", "skill2", ...],
  "experience_years": <integer>,
  "education_level": "<string>",
  "grammar_score": <integer 0-100>,
  "keywords_found": ["keyword1", "keyword2", ...],
  "missing_keywords": ["keyword1", "keyword2", ...]
}}"""

VACANCY_MATCHING_PROMPT = """You are an AI job matching expert. Calculate how well a candidate matches a job vacancy.

Candidate Profile:
- Skills: {candidate_skills}
- Experience: {candidate_experience}
- Education: {candidate_education}
- Location: {candidate_location}

Job Vacancy:
- Title: {vacancy_title}
- Requirements: {vacancy_requirements}
- Skills needed: {vacancy_skills}
- Location: {vacancy_location}
- Type: {vacancy_type}

Provide matching analysis as JSON:
{{
  "match_score": <integer 0-100>,
  "skill_match": <integer 0-100>,
  "experience_match": <integer 0-100>,
  "education_match": <integer 0-100>,
  "location_match": <integer 0-100>,
  "matching_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "explanation": "<detailed explanation in 2-3 sentences>"
}}"""

JOB_RECOMMENDATIONS_PROMPT = """You are an AI career advisor for students in Kazakhstan.
Rank the best HeadHunter job vacancies for a candidate using their job interests and academic transcript.

What the student is looking for:
{job_interests}

Academic transcript:
{transcript_text}

Available vacancies from HeadHunter (JSON array):
{vacancies_json}

Instructions:
- Match vacancies to the student's stated interests AND their education from the transcript.
- Prefer roles aligned with completed courses and the student's preferences.
- Return up to {limit} best matches sorted by match_score descending.
- Use only vacancy_id values from the provided list (exact string ids).
- Write explanation in {language_name}.

Return JSON:
{{
  "recommendations": [
    {{
      "vacancy_id": "<id from list>",
      "match_score": <integer 0-100>,
      "matching_skills": ["skill1", "skill2"],
      "missing_skills": ["skill1"],
      "explanation": "<2-3 sentences why this vacancy fits>"
    }}
  ]
}}"""

HH_SEARCH_QUERY_PROMPT = """You are an AI career assistant for students in Kazakhstan.
Build a concise HeadHunter (hh.kz) vacancy search query from the student's interests and academic transcript.

Student job interests:
{job_interests}

Academic transcript:
{transcript_text}

HeadHunter area ids (use when city is clear):
- 40 = all Kazakhstan
- 159 = Astana
- 160 = Almaty
- 161 = Shymkent

Rules:
- "text" must be a short search query (2-6 meaningful words) suitable for hh.kz search.
- Combine the student's interests with relevant education from the transcript.
- Prefer Russian or Kazakh keywords commonly used in vacancy titles in Kazakhstan.
- Do not include words like "ищу", "работу", "вакансию".
- Write reasoning in {language_name}.

Return JSON:
{{
  "text": "<hh search query>",
  "area": "<area id as string, default 40>",
  "reasoning": "<one sentence why this query fits>"
}}"""

COVER_LETTER_PROMPT = """You are a professional cover letter writer. Write a compelling cover letter.

Candidate:
- Name: {candidate_name}
- Skills: {candidate_skills}
- Experience: {candidate_experience}

Position: {position}
Company: {company}
Job Description: {job_description}
Tone: {tone}

Write a professional cover letter (200-350 words). Return as JSON:
{{
  "cover_letter": "<the full cover letter text>",
  "key_points": ["point1", "point2", "point3"]
}}"""

INTERVIEW_PREP_PROMPT = """You are an expert interview coach. Generate interview preparation materials.

Position: {position}
Company: {company}
Requirements: {requirements}
Difficulty: {difficulty}

Generate interview preparation as JSON:
{{
  "questions": [
    {{"question": "<question>", "category": "<technical|behavioral|situational>", "tip": "<answer tip>"}},
    ...
  ],
  "tips": ["tip1", "tip2", ...],
  "estimated_duration": <integer minutes>
}}

Generate 8-12 questions based on difficulty level."""

SKILL_GAP_PROMPT = """You are a career development advisor. Analyze the skill gap between current skills and target role requirements.

Current Skills: {current_skills}
Target Role: {target_role}

Provide analysis as JSON:
{{
  "current_skills": ["skill1", "skill2"],
  "required_skills": ["skill1", "skill2"],
  "gap_skills": ["skill1", "skill2"],
  "recommendations": [
    {{"skill": "<skill>", "resource": "<learning resource>", "estimated_hours": <integer>}},
    ...
  ],
  "estimated_learning_time": <total hours integer>,
  "priority_order": ["skill1", "skill2"]
}}"""

CAREER_COACH_PROMPT = """You are QalaJob AI Career Coach — an expert AI career advisor for students in Kazakhstan.
You help with:
- Career planning and advice
- Resume improvement tips
- Job search strategies
- Interview preparation
- Skill development roadmaps
- Industry insights

Be conversational, supportive, and practical.

CRITICAL LANGUAGE RULE: Reply entirely in {language_name}. Do not switch languages, even if the user writes in another language (unless quoting short technical terms).

Previous conversation:
{history}

User: {message}"""

EMPLOYER_ASSISTANT_SYSTEM = """You are QalaJob AI — an assistant for students and employers.

FOR STUDENTS:
- Resume review, career coaching, interview prep, internship advice, job search, skills

FOR EMPLOYERS:
- Vacancy generation, job descriptions, interview questions, candidate evaluation, hiring strategy

RULES:
1. CRITICAL: Reply entirely in {language_name}. Never answer in another language unless quoting short terms.
2. Use Markdown formatting.
3. Structure answers with clear headings and bullet points.
4. If asked for a vacancy, include title, company, location, responsibilities, requirements, skills, benefits, salary, how to apply.
5. If asked for interview questions, generate at least 10.
6. If asked for candidate evaluation, include strengths, weaknesses, hiring score, recommendation.
7. Keep responses professional. Do not invent company facts."""

RESUME_ENHANCE_PROMPT = """You are a professional resume writer. Enhance and improve the following resume while preserving the original information.

Original Resume:
{resume_text}

Improve the resume by:
1. Better structure and formatting
2. Stronger action verbs
3. Quantifiable achievements
4. Professional language
5. ATS-friendly keywords

CRITICAL: Write the enhanced resume entirely in {language_name}, unless the original is clearly in another language — then keep that language.
Return the enhanced resume text only, no JSON."""


VACANCY_GENERATION_PROMPT = """You are an HR expert. Generate a professional job vacancy description.

Position: {position}
Company: {company}
Location: {location}
Type: {job_type}
Salary Range: {salary_range}

Generate a complete vacancy as JSON:
{{
  "title": "<job title>",
  "description": "<detailed job description>",
  "requirements": "<requirements as bullet points>",
  "benefits": "<benefits as bullet points>",
  "skills": ["skill1", "skill2"]
}}"""


# ── Service Functions ───────────────────────────────────────────────

_client: Optional[object] = None


def get_client():
    global _client
    if _client is None:
        if getattr(settings, "LLM_HYBRID_ENABLED", False):
            from .llm.hybrid import HybridLLMClient

            _client = HybridLLMClient()
        else:
            from .llm.factory import get_openai_provider_client

            _client = get_openai_provider_client()
    return _client


def resolve_language_name(code: Optional[str] = None) -> str:
    """Map UI locale codes (kk/kz/ru/en) to a clear language name for prompts."""
    raw = (code or "kk").strip().lower().replace("_", "-")
    short = raw.split("-")[0]
    if short in ("ru", "rus"):
        return "Russian (русский)"
    if short in ("en", "eng"):
        return "English"
    return "Kazakh (қазақша)"


def analyze_resume(resume_text: str, target_role: str = "", language: str = "kk") -> dict:
    client = get_client()
    prompt = RESUME_ANALYSIS_PROMPT.format(
        resume_text=wrap_untrusted(resume_text, label="resume"),
        target_role=wrap_untrusted(target_role or "General", label="target_role"),
    )
    return client._call_json(
        [
            {"role": "system", "content": hardened_system("You are an expert HR analyst.")},
            {"role": "user", "content": prompt},
        ]
    )


def match_vacancy(candidate_data: dict, vacancy_data: dict) -> dict:
    client = get_client()
    prompt = VACANCY_MATCHING_PROMPT.format(
        candidate_skills=wrap_untrusted(candidate_data.get("skills", ""), label="candidate_skills"),
        candidate_experience=wrap_untrusted(candidate_data.get("experience", ""), label="candidate_experience"),
        candidate_education=wrap_untrusted(candidate_data.get("education", ""), label="candidate_education"),
        candidate_location=wrap_untrusted(candidate_data.get("location", ""), label="candidate_location"),
        vacancy_title=wrap_untrusted(vacancy_data.get("title", ""), label="vacancy_title"),
        vacancy_requirements=wrap_untrusted(vacancy_data.get("requirements", ""), label="vacancy_requirements"),
        vacancy_skills=wrap_untrusted(vacancy_data.get("skills", ""), label="vacancy_skills"),
        vacancy_location=wrap_untrusted(vacancy_data.get("location", ""), label="vacancy_location"),
        vacancy_type=wrap_untrusted(vacancy_data.get("type", ""), label="vacancy_type"),
    )
    return client._call_json(
        [
            {"role": "system", "content": hardened_system("You are an AI job matching expert.")},
            {"role": "user", "content": prompt},
        ]
    )


def recommend_jobs(
    candidate_data: dict,
    vacancies: list[dict],
    *,
    limit: int = 10,
    language: str = "ru",
    transcript_text: str = "",
) -> dict:
    client = get_client()
    language_name = resolve_language_name(language)

    prompt = JOB_RECOMMENDATIONS_PROMPT.format(
        job_interests=wrap_untrusted(candidate_data.get("job_interests", ""), label="job_interests"),
        transcript_text=wrap_untrusted(transcript_text or "No transcript data available.", label="transcript"),
        vacancies_json=wrap_untrusted(json.dumps(vacancies, ensure_ascii=False), label="vacancies_json"),
        limit=limit,
        language_name=language_name,
    )
    return client._call_json(
        [
            {"role": "system", "content": hardened_system("You are an AI career advisor.")},
            {"role": "user", "content": prompt},
        ],
        max_tokens=3000,
    )


def build_hh_search_query(
    candidate_data: dict,
    *,
    language: str = "ru",
    transcript_text: str = "",
) -> dict:
    client = get_client()
    language_name = resolve_language_name(language)

    prompt = HH_SEARCH_QUERY_PROMPT.format(
        job_interests=wrap_untrusted(candidate_data.get("job_interests", ""), label="job_interests"),
        transcript_text=wrap_untrusted(transcript_text or "No transcript data available.", label="transcript"),
        language_name=language_name,
    )
    return client._call_json(
        [
            {"role": "system", "content": hardened_system("You are an AI job search assistant.")},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
    )


def generate_cover_letter(
    candidate_data: dict,
    vacancy_data: dict,
    tone: str = "professional",
    language: str = "kk",
) -> dict:
    client = get_client()
    language_name = resolve_language_name(language)
    prompt = COVER_LETTER_PROMPT.format(
        candidate_name=wrap_untrusted(candidate_data.get("name", ""), label="candidate_name"),
        candidate_skills=wrap_untrusted(candidate_data.get("skills", ""), label="candidate_skills"),
        candidate_experience=wrap_untrusted(candidate_data.get("experience", ""), label="candidate_experience"),
        position=wrap_untrusted(vacancy_data.get("title", ""), label="position"),
        company=wrap_untrusted(vacancy_data.get("company", ""), label="company"),
        job_description=wrap_untrusted(vacancy_data.get("description", ""), label="job_description"),
        tone=wrap_untrusted(tone, label="tone"),
    )
    prompt += f"\n\nWrite the cover letter entirely in {language_name}."
    return client._call_json(
        [
            {"role": "system", "content": hardened_system("You are a professional cover letter writer.")},
            {"role": "user", "content": prompt},
        ]
    )


def prepare_interview(
    vacancy_data: dict,
    difficulty: str = "medium",
    language: str = "kk",
) -> dict:
    client = get_client()
    language_name = resolve_language_name(language)
    prompt = INTERVIEW_PREP_PROMPT.format(
        position=wrap_untrusted(vacancy_data.get("title", ""), label="position"),
        company=wrap_untrusted(vacancy_data.get("company", ""), label="company"),
        requirements=wrap_untrusted(vacancy_data.get("requirements", ""), label="requirements"),
        difficulty=wrap_untrusted(difficulty, label="difficulty"),
    )
    prompt += f"\n\nWrite all questions and tips entirely in {language_name}."
    return client._call_json(
        [
            {"role": "system", "content": hardened_system("You are an expert interview coach.")},
            {"role": "user", "content": prompt},
        ]
    )


def analyze_skill_gap(current_skills: list, target_role: str) -> dict:
    client = get_client()
    prompt = SKILL_GAP_PROMPT.format(
        current_skills=wrap_untrusted(
            ", ".join(current_skills) if current_skills else "None specified",
            label="current_skills",
        ),
        target_role=wrap_untrusted(target_role, label="target_role"),
    )
    return client._call_json(
        [
            {"role": "system", "content": hardened_system("You are a career development advisor.")},
            {"role": "user", "content": prompt},
        ]
    )


def career_coach_chat(
    message: str,
    history: list = None,
    language: str = "kk",
    *,
    history_trusted: bool = True,
) -> str:
    """Backward-compatible wrapper — resume assistant reply text only."""
    result = resume_assistant_chat(
        message,
        history=history,
        language=language,
        history_trusted=history_trusted,
    )
    return result.get("reply", "")


def _job_context_block(
    job_title: str = "",
    company: str = "",
    job_description: str = "",
) -> str:
    title = (job_title or "").strip()
    comp = (company or "").strip()
    desc = (job_description or "").strip()
    if not title and not comp and not desc:
        return ""
    return (
        "Target vacancy:\n"
        f"Role: {wrap_untrusted(title or '(not specified)', label='job_title')}\n"
        f"Company: {wrap_untrusted(comp or '(not specified)', label='company')}\n"
        f"Job description:\n{wrap_untrusted(desc or '(not specified)', label='job_description')}\n\n"
    )


def resume_assistant_chat(
    message: str,
    history: list = None,
    language: str = "kk",
    resume_draft: str = "",
    mode: str = "resume",
    resume_context: str = "",
    job_title: str = "",
    company: str = "",
    job_description: str = "",
    *,
    history_trusted: bool = False,
) -> dict:
    """
    Mode-aware writing assistant.
    mode: resume | cover_letter | interview | mock_interview
    Returns: {"reply": str, "document_draft": str | None}
    (resume_draft kept as alias of document_draft for compatibility)
    """
    client = get_client()
    language_name = resolve_language_name(language)
    mode = (mode or "resume").strip().lower()
    if mode not in ("resume", "cover_letter", "interview", "mock_interview"):
        mode = "resume"

    history_text = format_history_for_prompt(history, trusted=history_trusted)

    draft = (resume_draft or "").strip()
    draft_block = wrap_untrusted(
        draft if draft else "(empty)",
        label="document_draft",
    )

    job_ctx = _job_context_block(job_title, company, job_description)

    if mode == "cover_letter":
        system = (
            f"You are QalaJob Cover Letter AI for students and job seekers in Kazakhstan.\n"
            f"Help write and refine a cover letter / motivation letter for a specific role.\n"
            f"Ask for job title, company, and key requirements if missing.\n\n"
            f"CRITICAL: Reply entirely in {language_name}.\n\n"
            f"Always respond with VALID JSON only (no markdown fences):\n"
            f'{{"reply":"<short helpful message>",'
            f'"document_draft":"<full cover letter text, or null if unchanged>"}}\n\n'
            f"Rules:\n"
            f"- Put the FULL cover letter in document_draft when creating/updating it.\n"
            f"- Keep 200-350 words, professional, specific to the role.\n"
            f"- Do not invent employers or achievements — ask instead.\n"
            f"- document_draft must be ONLY the letter, never the resume.\n"
        )
        context_block = (
            f"User resume (context only — do not copy wholesale):\n"
            f"{wrap_untrusted((resume_context or '').strip() or '(none)', label='resume_context')}\n\n"
            if (resume_context or "").strip()
            else ""
        )
        user_content = (
            f"{job_ctx}"
            f"{context_block}"
            f"Current cover letter draft:\n{draft_block}\n\n"
            f"Conversation so far:\n{history_text or '(none)'}\n\n"
            f"User message:\n{wrap_untrusted(message, label='user_message')}"
        )
    elif mode == "mock_interview":
        target_role = (job_title or "").strip() or "the role stated by the candidate"
        target_company = (company or "").strip() or "(not specified)"
        target_jd = (job_description or "").strip() or "(not provided)"
        system = (
            f"You are a realistic hiring interviewer for a mock interview rehearsal.\n"
            f"Conduct a live practice interview with the candidate.\n\n"
            f"=== AUTHORITATIVE TARGET ROLE (DO NOT CHANGE) ===\n"
            f"Position: {target_role}\n"
            f"Company: {target_company}\n"
            f"Job details: {target_jd}\n"
            f"You MUST interview ONLY for this position. Never invent another job "
            f"(e.g. waiter, cashier, driver) unless the user EXPLICITLY asks to change the role.\n"
            f"If prior conversation mentioned a different role, apologize briefly and continue "
            f"for the AUTHORITATIVE TARGET ROLE above.\n"
            f"===============================================\n\n"
            f"CRITICAL: Reply entirely in {language_name}.\n\n"
            f"Always respond with VALID JSON only (no markdown fences):\n"
            f'{{"reply":"<what you say to the candidate>",'
            f'"document_draft":"<updated scorecard / session notes, or null if unchanged>"}}\n\n'
            f"Behavior rules:\n"
            f"1. On start: greet briefly, explicitly confirm the TARGET ROLE ({target_role}), "
            f"then ask ONE opening question relevant to that role.\n"
            f"2. Ask ONLY ONE question at a time. Wait for the answer.\n"
            f"3. After each answer: short feedback (1-3 bullets), then the NEXT question for this role.\n"
            f"4. Mix technical, behavioral (STAR), and motivation questions for {target_role}.\n"
            f"5. About 5-8 questions, then wrap up with score 1-10, strengths, gaps, 3 tips.\n"
            f"6. If user says stop/finish/end — wrap up immediately.\n"
            f"7. Stay in interviewer persona; do not dump a full question list at once.\n"
            f"8. Scorecard in document_draft must list Role: {target_role}.\n"
            f"9. Use resume context if provided; do not invent fake experience.\n"
            f"10. Candidate name may appear in resume; greet them politely but still interview "
            f"for {target_role} only.\n"
        )
        context_block = (
            f"Candidate resume (context):\n"
            f"{wrap_untrusted((resume_context or '').strip() or '(none)', label='resume_context')}\n\n"
            if (resume_context or "").strip()
            else ""
        )
        user_content = (
            f"TARGET ROLE: {wrap_untrusted(target_role, label='job_title')}\n"
            f"COMPANY: {wrap_untrusted(target_company, label='company')}\n"
            f"JOB DETAILS: {wrap_untrusted(target_jd, label='job_description')}\n\n"
            f"{context_block}"
            f"Current session scorecard:\n{draft_block}\n\n"
            f"Conversation so far:\n{history_text or '(none)'}\n\n"
            f"Candidate message:\n{wrap_untrusted(message, label='user_message')}"
        )
    elif mode == "interview":
        target_role = (job_title or "").strip() or "the role from the vacancy"
        target_company = (company or "").strip() or "(not specified)"
        target_jd = (job_description or "").strip() or "(not provided)"
        system = (
            f"You are QalaJob Interview Coach for students and job seekers in Kazakhstan.\n"
            f"You run a live interview rehearsal for a specific vacancy — one question at a time.\n\n"
            f"=== TARGET ROLE ===\n"
            f"Position: {target_role}\n"
            f"Company: {target_company}\n"
            f"Job details: {target_jd}\n"
            f"Interview ONLY for this role.\n"
            f"===================\n\n"
            f"CRITICAL: Reply entirely in {language_name}.\n\n"
            f"Always respond with VALID JSON only (no markdown fences):\n"
            f'{{"reply":"<what you say to the candidate>",'
            f'"document_draft":"<updated rehearsal notes, or null if unchanged>"}}\n\n'
            f"Behavior:\n"
            f"1. On start / vacancy loaded: briefly confirm the role ({target_role}), then ask ONE "
            f"first interview question relevant to this vacancy. Do NOT list many questions.\n"
            f"2. Ask ONLY ONE question per reply. Wait for the answer.\n"
            f"3. After each answer: 1-3 short feedback bullets, then the NEXT question.\n"
            f"4. Mix technical, behavioral (STAR), and motivation questions for {target_role}.\n"
            f"5. Stay in interviewer persona in reply. Put a running Q/A notes in document_draft.\n"
            f"6. Do not invent fake experience from the resume.\n"
        )
        context_block = (
            f"User resume (context):\n"
            f"{wrap_untrusted((resume_context or '').strip() or '(none)', label='resume_context')}\n\n"
            if (resume_context or "").strip()
            else ""
        )
        user_content = (
            f"{job_ctx}"
            f"{context_block}"
            f"Current interview rehearsal notes:\n{draft_block}\n\n"
            f"Conversation so far:\n{history_text or '(none)'}\n\n"
            f"User message:\n{wrap_untrusted(message, label='user_message')}"
        )
    else:
        system = (
            f"You are QalaJob Resume AI — an expert resume-writing assistant for students and job seekers "
            f"in Kazakhstan.\n\n"
            f"Your ONLY focus: help the user write, structure, and improve their resume/CV.\n"
            f"You can: collect experience/education/skills, rewrite sections, suggest stronger wording, "
            f"adapt the resume to a target role, and produce a complete polished resume.\n"
            f"Do NOT digress into general chat unrelated to resumes.\n\n"
            f"CRITICAL: Reply entirely in {language_name}.\n\n"
            f"Always respond with VALID JSON only (no markdown fences):\n"
            f'{{"reply":"<short helpful message to the user>",'
            f'"document_draft":"<full updated resume text, or null if unchanged>"}}\n\n'
            f"Rules for document_draft:\n"
            f"- If you create or improve the resume, put the FULL resume text in document_draft.\n"
            f"- Use clear section headings (e.g. Summary, Experience, Education, Skills, Projects).\n"
            f"- If you only ask a clarifying question and do not change the resume, set document_draft to null.\n"
            f"- Never invent fake employers, degrees, or dates — ask the user instead.\n"
        )
        user_content = (
            f"{job_ctx}"
            f"Current resume draft:\n{draft_block if draft else '(empty — help the user create a resume from scratch)'}\n\n"
            f"Conversation so far:\n{history_text or '(none)'}\n\n"
            f"User message:\n{wrap_untrusted(message, label='user_message')}"
        )

    raw = client._call(
        [
            {"role": "system", "content": hardened_system(system)},
            {"role": "user", "content": user_content},
        ],
        temperature=0.45 if mode == "mock_interview" else 0.6,
        max_tokens=3500,
    )

    if not raw:
        return {
            "reply": "I'm temporarily unavailable. Please try again.",
            "document_draft": None,
            "resume_draft": None,
        }

    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [line for line in lines if not line.strip().startswith("```")]
        cleaned = "\n".join(lines)

    try:
        data = json.loads(cleaned)
        reply = sanitize_reply_text(str(data.get("reply") or ""))
        updated = sanitize_document_draft(
            data.get("document_draft", data.get("resume_draft", None))
        )
        if not reply:
            reply = "Готово." if language_name.startswith("Russian") else (
                "Дайын." if "Kazakh" in language_name else "Done."
            )
        return {
            "reply": reply,
            "document_draft": updated,
            "resume_draft": updated,
        }
    except json.JSONDecodeError:
        return {
            "reply": sanitize_reply_text(cleaned),
            "document_draft": None,
            "resume_draft": None,
        }


def structure_resume_from_text(raw_text: str, language: str = "kk", source: str = "paste") -> dict:
    """
    Turn messy paste / LinkedIn export / PDF extract into a structured resume.
    Returns: {"resume": str, "notes": str}
    """
    client = get_client()
    language_name = resolve_language_name(language)
    text = (raw_text or "").strip()
    if not text:
        return {"resume": "", "notes": "Empty input"}

    system = (
        f"You convert messy profile/resume text into a clean structured resume.\n"
        f"Source hint: {source}.\n"
        f"CRITICAL: Output the resume entirely in {language_name}.\n"
        f"Do NOT invent employers, degrees, dates, or skills that are not implied by the input.\n"
        f"Organize into clear sections: Summary, Experience, Education, Skills, Projects, Languages "
        f"(omit empty sections).\n"
        f"Return VALID JSON only:\n"
        f'{{"resume":"<full structured resume text>","notes":"<short note about what you inferred>"}}'
    )
    raw = client._call(
        [
            {"role": "system", "content": hardened_system(system)},
            {
                "role": "user",
                "content": wrap_untrusted(text, label="raw_resume_text"),
            },
        ],
        temperature=0.3,
        max_tokens=3500,
    )
    if not raw:
        return {"resume": text, "notes": "AI unavailable — returned original text"}

    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [line for line in lines if not line.strip().startswith("```")]
        cleaned = "\n".join(lines)

    try:
        data = json.loads(cleaned)
        resume = str(data.get("resume") or "").strip() or text
        notes = str(data.get("notes") or "").strip()
        return {"resume": resume, "notes": notes}
    except json.JSONDecodeError:
        return {"resume": cleaned or text, "notes": ""}


def generate_cover_letter_freeform(
    resume_text: str,
    job_title: str,
    company: str,
    job_description: str = "",
    tone: str = "professional",
    language: str = "kk",
) -> dict:
    candidate_data = {
        "name": "Candidate",
        "skills": "",
        "experience": (resume_text or "")[:4000],
    }
    vacancy_data = {
        "title": job_title or "Position",
        "company": company or "Company",
        "description": job_description or "",
    }
    return generate_cover_letter(
        candidate_data,
        vacancy_data,
        tone=tone or "professional",
        language=language,
    ) or {}


def prepare_interview_freeform(
    job_title: str,
    company: str = "",
    requirements: str = "",
    difficulty: str = "medium",
    language: str = "kk",
) -> dict:
    vacancy_data = {
        "title": job_title or "Position",
        "company": company or "",
        "requirements": requirements or "",
    }
    return prepare_interview(
        vacancy_data,
        difficulty=difficulty or "medium",
        language=language,
    ) or {}


def assistant_chat(message: str, history: list = None, language: str = "kk") -> str:
    """General / employer assistant chat."""
    client = get_client()
    language_name = resolve_language_name(language)
    system = hardened_system(
        "You are QalaJob AI — an assistant for students and employers.\n\n"
        "FOR STUDENTS: resume review, career coaching, interview prep, job search, skills.\n"
        "FOR EMPLOYERS: vacancy generation, job descriptions, interview questions, "
        "candidate evaluation, hiring strategy.\n\n"
        f"RULES:\n"
        f"1. CRITICAL: Reply entirely in {language_name}. Never answer in another language "
        "unless quoting short terms.\n"
        "2. Use Markdown formatting.\n"
        "3. Structure answers with clear headings and bullet points.\n"
        "4. Keep responses professional. Do not invent company facts."
    )
    messages: list[dict] = [{"role": "system", "content": system}]
    safe_history = sanitize_client_history(history)
    for msg in safe_history:
        messages.append(
            {
                "role": "user",
                "content": wrap_untrusted(msg["content"], label="prior_user_message"),
            }
        )
    messages.append(
        {
            "role": "user",
            "content": wrap_untrusted(str(message), label="user_message"),
        }
    )
    return client._call(messages, temperature=0.7, max_tokens=3000)


def enhance_resume(resume_text: str, language: str = "kk") -> str:
    client = get_client()
    language_name = resolve_language_name(language)
    prompt = (
        "You are a professional resume writer. Enhance and improve the following resume "
        "while preserving the original information.\n\n"
        f"Original Resume:\n{wrap_untrusted(resume_text, label='resume')}\n\n"
        "Improve structure, action verbs, achievements, professional language, and ATS keywords.\n"
        f"CRITICAL: Prefer writing the enhanced resume in {language_name}, "
        "unless the original is clearly in another language — then keep that language.\n"
        "Return the enhanced resume text only, no JSON."
    )
    return client._call(
        [
            {
                "role": "system",
                "content": hardened_system(
                    f"You are a professional resume writer. "
                    f"Prefer writing in {language_name}."
                ),
            },
            {"role": "user", "content": prompt},
        ]
    )


def generate_vacancy_description(data: dict) -> dict:
    client = get_client()
    prompt = VACANCY_GENERATION_PROMPT.format(
        position=wrap_untrusted(data.get("position", ""), label="position"),
        company=wrap_untrusted(data.get("company", ""), label="company"),
        location=wrap_untrusted(data.get("location", ""), label="location"),
        job_type=wrap_untrusted(data.get("job_type", "Full Time"), label="job_type"),
        salary_range=wrap_untrusted(data.get("salary_range", "Negotiable"), label="salary_range"),
    )
    return client._call_json(
        [
            {"role": "system", "content": hardened_system("You are an HR expert.")},
            {"role": "user", "content": prompt},
        ]
    )


def adapt_resume_to_vacancy(
    resume_text: str,
    vacancy_text: str,
    language: str = "kk",
) -> dict:
    """
    Tailor a resume to a specific vacancy.
    Returns: { adapted_resume, match_notes, missing_skills }
    """
    client = get_client()
    language_name = resolve_language_name(language)
    system = (
        f"You tailor resumes to a specific job vacancy.\n"
        f"CRITICAL: Write the adapted resume entirely in {language_name}.\n"
        f"Do NOT invent employers, degrees, dates, or fake achievements.\n"
        f"Reorder and rephrase existing experience to match the vacancy.\n"
        f"Highlight relevant skills; mention gaps honestly in notes.\n"
        f"Return VALID JSON only:\n"
        f'{{"adapted_resume":"<full resume text>",'
        f'"match_notes":"<short explanation of changes>",'
        f'"missing_skills":["skill1","skill2"]}}'
    )
    user = (
        f"VACANCY:\n{wrap_untrusted(vacancy_text or '', label='vacancy')}\n\n"
        f"CURRENT RESUME:\n{wrap_untrusted(resume_text or '(empty — create a strong draft from vacancy keywords only using placeholders for unknown facts)', label='resume')}"
    )
    raw = client._call(
        [
            {"role": "system", "content": hardened_system(system)},
            {"role": "user", "content": user},
        ],
        temperature=0.45,
        max_tokens=3500,
    )
    if not raw:
        return {
            "adapted_resume": resume_text or "",
            "match_notes": "AI unavailable",
            "missing_skills": [],
        }

    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [line for line in lines if not line.strip().startswith("```")]
        cleaned = "\n".join(lines)

    try:
        data = json.loads(cleaned)
        adapted = str(data.get("adapted_resume") or "").strip() or (resume_text or "")
        notes = str(data.get("match_notes") or "").strip()
        missing = data.get("missing_skills") or []
        if not isinstance(missing, list):
            missing = []
        missing = [str(x) for x in missing if x]
        return {
            "adapted_resume": adapted,
            "match_notes": notes,
            "missing_skills": missing,
        }
    except json.JSONDecodeError:
        return {
            "adapted_resume": cleaned or resume_text or "",
            "match_notes": "",
            "missing_skills": [],
        }
