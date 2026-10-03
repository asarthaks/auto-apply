"""
Pydantic state schema for the job-apply pipeline.

Why this file exists:
- Every node reads from and writes to a single shared state object.
  Defining it in one place means schema changes are visible, and every
  node gets type hints for free.
- Pydantic models (not plain dicts) give us validation on assignment
  and a single source of truth for field names. If a node tries to
  write `state.jop` instead of `state.job`, Pydantic catches it.
- Start SMALL. This file will grow in later steps. Resist adding
  fields for things you don't yet need (cover letter, pdf paths, etc.)
  — YAGNI applies hard here.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class JobPosting(BaseModel):
    """
    Structured representation of a parsed job posting.

    This is the output of parse_job and the input to every downstream
    node (tailor, cover letter, etc.). Keep field names short and
    lowercase; keep field types simple (str, list[str], Optional).
    The LLM will populate this from raw page text.
    """

    # TODO: define fields. Suggested (you decide exact names):
    #   - url: str                         (copied from state, for traceability)
    #   - title: str                       (job title, e.g. "Research Engineer")
    #   - company: str                     (e.g. "Anthropic")
    #   - location: str | None             (can be None; many postings omit)
    #   - seniority: str | None            ("junior"/"mid"/"senior"/"staff"/None)
    #   - employment_type: str | None      ("full-time"/"contract"/None)
    #   - must_have: list[str]             (hard requirements)
    #   - nice_to_have: list[str]          (preferred/bonus qualifications)
    #   - keywords: list[str]              (technologies, tools, domains — for the tailor)
    #   - responsibilities: list[str]      (what the role does day-to-day)
    #
    # Use Field(default_factory=list) for list fields with no default.
    # Use `str | None = None` for optional scalars.
    url: str
    title: str
    company: str
    location: str
    seniority: str
    employment_type: str
    must_have: list[str]
    nice_to_have: list[str]
    keywords: list[str]
    responsibilities: list[str]
    job_description_complete: str
    pass


class AppState(BaseModel):
    """
    The shared pipeline state. Flows through every node.

    Each node:
    1. Reads the fields it needs.
    2. Computes something.
    3. Returns a new AppState with the computed fields set.

    For step 2, this holds only the job URL, the raw fetched text,
    the parsed JobPosting, and an error list. Later steps will add
    `tailored_resume`, `cover_letter`, `pdf_paths`, etc.
    """

    job_url: str
    raw_text: str | None = None
    job: JobPosting | None = None
    errors: list[str] = Field(default_factory=list)

    # Why a list of errors instead of raising exceptions:
    # In a multi-node pipeline, you often want to continue past a
    # soft failure (e.g., couldn't extract seniority) rather than
    # crash the whole run. Nodes append to `errors` and keep going.
    # Hard failures (network down, API key invalid) can still raise.