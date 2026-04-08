"""
Step 1 smoke test.

Verifies that:
1. Config loaded successfully (no missing env vars).
2. Each configured provider responds to a trivial chat completion.
3. LangSmith receives traces (check the dashboard after running).

Run from inside the container:
    docker compose run --rm app python -m src.smoke_test

Exit code is non-zero if any provider fails, so you can wire this
into CI later.
"""

from __future__ import annotations

import sys
import traceback
from typing import List, Tuple

from src.llm import get_client, Provider


PROVIDERS_TO_TEST: List[Provider] = ["local"]


def test_provider(provider: Provider) -> Tuple[bool, str]:
    """
    Make one tiny chat completion call. Return (success, message).

    We keep the prompt deterministic and the output tiny because we are
    testing connectivity, not model quality. Temperature=0 makes runs
    reproducible. max_tokens=20 keeps it fast and cheap.
    """
    try:
        client, model = get_client(provider)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Reply with exactly this text and nothing else: "
                        f"HELLO FROM {provider.upper()}"
                    ),
                }
            ],
            temperature=0,
            max_tokens=20,
        )
        content = (resp.choices[0].message.content or "").strip()
        return True, content
    except Exception as e:
        # Full traceback so you can actually debug the failure.
        return False, f"{type(e).__name__}: {e}\n{traceback.format_exc()}"


def main() -> int:
    print("=" * 60)
    print("SMOKE TEST — verifying all LLM providers")
    print("=" * 60)

    results = []
    for provider in PROVIDERS_TO_TEST:
        print(f"\n[{provider}] calling...")
        ok, msg = test_provider(provider)
        if ok:
            print(f"[{provider}] OK -> {msg!r}")
        else:
            print(f"[{provider}] FAIL")
            print(msg)
        results.append((provider, ok))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for provider, ok in results:
        status = "OK  " if ok else "FAIL"
        print(f"  {status}  {provider}")

    all_ok = all(ok for _, ok in results)
    if all_ok:
        print("\nAll providers working. Check LangSmith dashboard for traces:")
        print("  https://smith.langchain.com")
    else:
        print("\nOne or more providers failed. See errors above.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())