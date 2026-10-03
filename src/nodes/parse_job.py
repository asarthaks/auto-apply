"""
Node: parse_job

Takes raw job posting text and returns a structured JobPosting.
This is the first LLM node in the pipeline.

Why Gemini Flash specifically for this node:
- Free tier, so iterating on the prompt costs nothing.
- Supports json_schema structured output, so we get valid Pydantic
  objects without a retry loop.
- Fast (~2-5 seconds), so the dev loop stays tight.
"""

from __future__ import annotations

import json

from src.llm import get_client
from src.state import AppState, JobPosting


# Keep this prompt short. With structured output, the model doesn't
# need a big schema description in the prompt — the schema itself
# enforces structure. The prompt's job is to tell the model WHAT
# to extract and any nuances of interpretation.
SYSTEM_PROMPT = """\
You are a precise job posting parser. Extract structured information
from the job posting text provided by the user. Follow these rules:

1. Use ONLY information present in the text. Never invent details.
2. If a field is not stated, return an empty list (for list fields)
   or null (for optional scalar fields). Never guess.
3. `must_have` vs `nice_to_have`: look for section headers like
   "Requirements" / "Minimum qualifications" vs "Preferred" / "Nice
   to have" / "Bonus". If unclear, default to must_have.
4. `keywords` should be concrete technologies, tools, and domains
   mentioned anywhere in the posting (e.g. "Python", "PyTorch",
   "distributed systems", "RLHF"). NOT soft skills.
5. `seniority`: infer from title and years-of-experience requirements.
   Use one of: "junior", "mid", "senior", "staff", "principal", or null.
"""


def run(state: AppState) -> AppState:
    """
    Parse state.raw_text into state.job. On LLM or validation failure,
    append to state.errors and leave state.job as None.
    """
    if not state.raw_text:
        state.errors.append("parse_job: no raw_text in state; did fetch_job run?")
        return state

    # TODO 1: Get the Gemini client and model name.
    # client, model = ...

    # TODO 2: Build the json_schema structure for response_format.
    # Pydantic gives you the schema for free:
    #     schema = JobPosting.model_json_schema()
    # The OpenAI SDK wants it wrapped like this:
    #     response_format = {
    #         "type": "json_schema",
    #         "json_schema": {
    #             "name": "JobPosting",
    #             "schema": schema,
    #             "strict": True,  # enforce exact match
    #         },
    #     }
    # Gemini may reject the schema if it contains $defs or $ref.
    # If you get a 400, call strip_schema_refs(schema) (write a tiny
    # helper) or set `strict=False` and validate in Python.

    # TODO 3: Call the model.
    # Messages: [system, user] where user content is state.raw_text.
    # Temperature: 0 (we want deterministic extraction).
    # max_tokens: generous — job postings can produce long output.
    #     Try 2000 and adjust if you see truncation.
    # response_format: the dict you built above.

    # TODO 4: Parse the response.
    # raw = response.choices[0].message.content
    # On success, `raw` is a JSON string matching the schema.
    # Validate with:
    #     parsed = JobPosting.model_validate_json(raw)
    # Catch pydantic.ValidationError and json.JSONDecodeError; on
    # failure, append to state.errors and return state.

    # TODO 5: Set the url field on the parsed object (the LLM doesn't
    # see it, so it can't set it itself) and write to state.
    # parsed.url = state.job_url
    # state.job = parsed
    # return state

    return state  # remove once TODOs are filled in