"""
Node: fetch_job

Fetches a job posting URL and extracts the readable main content.
No LLM involved — pure HTTP + HTML cleaning.

Why separate this from parse_job:
- Different failure modes (network vs LLM).
- Different latency profiles (fetch is fast, parse is slow).
- Easier to cache fetch results during development so you're not
  hammering the same URL 50 times while iterating on the prompt.
"""

from __future__ import annotations

import httpx
import trafilatura

from src.state import AppState


# Pretending to be a real browser avoids the 20% of sites that
# reject requests with a "python-httpx" user agent. Not evasion,
# just compatibility.
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 20.0  # seconds


def run(state: AppState) -> AppState:
    """
    Fetch state.job_url, extract the main content, write it to
    state.raw_text. On failure, append to state.errors and return
    the state unchanged otherwise.

    Returns the SAME AppState object with mutations, OR a new one
    via state.model_copy(update=...). Either works — pick one style
    and use it consistently across all nodes.
    """
    url = state.job_url

    # TODO 1: Fetch the URL with httpx.
    # Use httpx.Client (sync, not async — we'll add async later if
    # it matters). Set `headers={"User-Agent": USER_AGENT}`,
    # `timeout=REQUEST_TIMEOUT`, and `follow_redirects=True`.
    # Catch httpx.HTTPError and network exceptions; on failure,
    # append to state.errors (e.g. f"fetch_job: {type(e).__name__}: {e}")
    # and return state early.
    html: str = ""  # replace with the real fetch

    # TODO 2: Check the HTTP status. If it's not 2xx, append an error
    # to state.errors and return state.
    # Hint: `response.raise_for_status()` inside the try block is the
    # idiomatic way.

    # TODO 3: Extract the main content with trafilatura.
    # `trafilatura.extract(html)` returns the cleaned text or None.
    # If None, append an error and return state.
    # Optional kwargs worth knowing:
    #   include_comments=False  (default True — we want False)
    #   include_tables=True     (job postings often use tables)
    #   favor_precision=True    (fewer false positives on navbar junk)
    text: str | None = None  # replace with the real extract

    # TODO 4: Sanity check the extracted text. If it's under, say,
    # 200 characters, something went wrong (wrong page, bot block,
    # empty body). Append an error and return state.

    # TODO 5: Write the text to state and return.
    state.raw_text = text
    return state