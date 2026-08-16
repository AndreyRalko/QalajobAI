"""
OpenAI client for QalaJob AI.
Uses the Chat Completions HTTP API via requests (avoids openai/httpx SDK conflicts).
"""

from __future__ import annotations

import json
import logging
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger("apps")

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIClient:
    """Thin wrapper around the OpenAI Chat Completions API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        raw_key = api_key if api_key is not None else getattr(settings, "OPENAI_API_KEY", "")
        self.api_key = str(raw_key or "").strip().strip('"').strip("'")
        self.model = model or getattr(settings, "OPENAI_MODEL", "gpt-4o-mini") or "gpt-4o-mini"

    def _call(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not configured — demo response")
            last_user = next(
                (m.get("content", "") for m in reversed(messages) if m.get("role") == "user"),
                "",
            )
            return (
                "[Demo mode] Configure OPENAI_API_KEY in backend/.env for live AI. "
                f"You asked: {str(last_user)[:200]}"
            )

        try:
            response = requests.post(
                OPENAI_CHAT_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=60,
            )
            if response.status_code >= 400:
                logger.error(
                    "OpenAI API error %s: %s",
                    response.status_code,
                    response.text[:500],
                )
                return ""

            data = response.json()
            return (data["choices"][0]["message"]["content"] or "").strip()
        except Exception as exc:
            logger.error("OpenAI API error: %s", exc)
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

_client: Optional[OpenAIClient] = None


def get_client() -> OpenAIClient:
    global _client
    if _client is None:
        _client = OpenAIClient()
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
        resume_text=resume_text,
        target_role=target_role or "General",
    )
    return client._call_json(
        [
            {"role": "system", "content": "You are an expert HR analyst."},
            {"role": "user", "content": prompt},
        ]
    )


def match_vacancy(candidate_data: dict, vacancy_data: dict) -> dict:
    client = get_client()
    prompt = VACANCY_MATCHING_PROMPT.format(
        candidate_skills=candidate_data.get("skills", ""),
        candidate_experience=candidate_data.get("experience", ""),
        candidate_education=candidate_data.get("education", ""),
        candidate_location=candidate_data.get("location", ""),
        vacancy_title=vacancy_data.get("title", ""),
        vacancy_requirements=vacancy_data.get("requirements", ""),
        vacancy_skills=vacancy_data.get("skills", ""),
        vacancy_location=vacancy_data.get("location", ""),
        vacancy_type=vacancy_data.get("type", ""),
    )
    return client._call_json(
        [
            {"role": "system", "content": "You are an AI job matching expert."},
            {"role": "user", "content": prompt},
        ]
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
        candidate_name=candidate_data.get("name", ""),
        candidate_skills=candidate_data.get("skills", ""),
        candidate_experience=candidate_data.get("experience", ""),
        position=vacancy_data.get("title", ""),
        company=vacancy_data.get("company", ""),
        job_description=vacancy_data.get("description", ""),
        tone=tone,
    )
    prompt += f"\n\nWrite the cover letter entirely in {language_name}."
    return client._call_json(
        [
            {"role": "system", "content": "You are a professional cover letter writer."},
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
        position=vacancy_data.get("title", ""),
        company=vacancy_data.get("company", ""),
        requirements=vacancy_data.get("requirements", ""),
        difficulty=difficulty,
    )
    prompt += f"\n\nWrite all questions and tips entirely in {language_name}."
    return client._call_json(
        [
            {"role": "system", "content": "You are an expert interview coach."},
            {"role": "user", "content": prompt},
        ]
    )


def analyze_skill_gap(current_skills: list, target_role: str) -> dict:
    client = get_client()
    prompt = SKILL_GAP_PROMPT.format(
        current_skills=", ".join(current_skills) if current_skills else "None specified",
        target_role=target_role,
    )
    return client._call_json(
        [
            {"role": "system", "content": "You are a career development advisor."},
            {"role": "user", "content": prompt},
        ]
    )


def career_coach_chat(message: str, history: list = None, language: str = "kk") -> str:
    """Backward-compatible wrapper — resume assistant reply text only."""
    result = resume_assistant_chat(message, history=history, language=language)
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
        f"Role: {title or '(not specified)'}\n"
        f"Company: {comp or '(not specified)'}\n"
        f"Job description:\n{desc or '(not specified)'}\n\n"
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

    history_text = ""
    if history:
        for msg in history[-12:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_text += f"{role}: {content}\n"

    draft = (resume_draft or "").strip()
    draft_block = draft if draft else "(empty)"

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
            f"User resume (context only — do not copy wholesale):\n{(resume_context or '').strip() or '(none)'}\n\n"
            if (resume_context or "").strip()
            else ""
        )
        user_content = (
            f"{job_ctx}"
            f"{context_block}"
            f"Current cover letter draft:\n{draft_block}\n\n"
            f"Conversation so far:\n{history_text or '(none)'}\n\n"
            f"User message:\n{message}"
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
            f"Candidate resume (context):\n{(resume_context or '').strip() or '(none)'}\n\n"
            if (resume_context or "").strip()
            else ""
        )
        user_content = (
            f"TARGET ROLE: {target_role}\n"
            f"COMPANY: {target_company}\n"
            f"JOB DETAILS: {target_jd}\n\n"
            f"{context_block}"
            f"Current session scorecard:\n{draft_block}\n\n"
            f"Conversation so far:\n{history_text or '(none)'}\n\n"
            f"Candidate message:\n{message}"
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
            f"User resume (context):\n{(resume_context or '').strip() or '(none)'}\n\n"
            if (resume_context or "").strip()
            else ""
        )
        user_content = (
            f"{job_ctx}"
            f"{context_block}"
            f"Current interview rehearsal notes:\n{draft_block}\n\n"
            f"Conversation so far:\n{history_text or '(none)'}\n\n"
            f"User message:\n{message}"
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
            f"User message:\n{message}"
        )

    raw = client._call(
        [
            {"role": "system", "content": system},
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
        reply = str(data.get("reply") or "").strip()
        updated = data.get("document_draft", data.get("resume_draft", None))
        if updated is not None:
            updated = str(updated).strip() or None
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
            "reply": cleaned,
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
            {"role": "system", "content": system},
            {"role": "user", "content": text[:12000]},
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
    system = (
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
    if history:
        for msg in history[-10:]:
            role = msg.get("role", "user")
            if role not in ("user", "assistant"):
                role = "user"
            messages.append({"role": role, "content": str(msg.get("content", ""))})
    messages.append({"role": "user", "content": str(message)})
    return client._call(messages, temperature=0.7, max_tokens=3000)


def enhance_resume(resume_text: str, language: str = "kk") -> str:
    client = get_client()
    language_name = resolve_language_name(language)
    prompt = (
        "You are a professional resume writer. Enhance and improve the following resume "
        "while preserving the original information.\n\n"
        f"Original Resume:\n{resume_text}\n\n"
        "Improve structure, action verbs, achievements, professional language, and ATS keywords.\n"
        f"CRITICAL: Prefer writing the enhanced resume in {language_name}, "
        "unless the original is clearly in another language — then keep that language.\n"
        "Return the enhanced resume text only, no JSON."
    )
    return client._call(
        [
            {
                "role": "system",
                "content": (
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
        position=data.get("position", ""),
        company=data.get("company", ""),
        location=data.get("location", ""),
        job_type=data.get("job_type", "Full Time"),
        salary_range=data.get("salary_range", "Negotiable"),
    )
    return client._call_json(
        [
            {"role": "system", "content": "You are an HR expert."},
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
        f"VACANCY:\n{(vacancy_text or '')[:8000]}\n\n"
        f"CURRENT RESUME:\n{(resume_text or '')[:8000] or '(empty — create a strong draft from vacancy keywords only using placeholders for unknown facts)'}"
    )
    raw = client._call(
        [
            {"role": "system", "content": system},
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
