"""
Step 2 driver. Temporary scaffolding — delete in step 3 when
LangGraph takes over orchestration.

Usage:
    docker compose run --rm app python -m src.run_step2 <job_url>
"""

from __future__ import annotations

import sys

from src.state import AppState
from src.nodes import fetch_job, parse_job


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python -m src.run_step2 <job_url>", file=sys.stderr)
        return 1

    url = sys.argv[1]
    state = AppState(job_url=url)

    print(f"[1/2] fetch_job: {url}")
    state = fetch_job.run(state)
    if state.errors:
        print(f"  errors: {state.errors}")
        return 1
    print(f"  ok, {len(state.raw_text or '')} chars extracted")

    print("[2/2] parse_job")
    state = parse_job.run(state)
    if state.errors:
        print(f"  errors: {state.errors}")
        return 1
    if state.job is None:
        print("  parse returned no job")
        return 1

    print("\n=== PARSED JOB ===")
    print(state.job.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())