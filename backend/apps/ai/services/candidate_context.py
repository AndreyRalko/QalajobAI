def build_candidate_context(user, job_interests: str = "") -> dict:
    """Build AI context from the student's own search query only."""
    return {
        "job_interests": (job_interests or "").strip(),
    }
