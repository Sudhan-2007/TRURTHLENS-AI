#!/usr/bin/env python3
"""Post-deployment smoke test for TruthLens AI.

Checks the health surface and core public endpoints against a live deployment:

    python deployment/scripts/smoke_test.py --base https://example.com

Returns exit code 0 when every check passes, 1 otherwise.
"""
import argparse
import json
import sys
import urllib.request

CHECKS: list[tuple[str, str, tuple[str, ...]]] = [
    ("frontend", "/", ("<!doctype html", "<html", "TruthLens AI")),
    ("backend_health", "/health", ("status",)),
    ("backend_api_health", "/api/health", ("database",)),
    ("database_health", "/api/health/db", ("connected",)),
    ("metrics", "/api/metrics", ("truthlens_http_requests_total",)),
]


def get(url: str, timeout: int = 10) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "TruthLens-smoke/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        return 0, str(exc)


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke test a TruthLens deployment.")
    parser.add_argument("--base", default="http://localhost", help="Base URL of the deployment")
    parser.add_argument("--timeout", type=int, default=10)
    args = parser.parse_args()

    failed = 0
    for name, path, needles in CHECKS:
        url = args.base.rstrip("/") + path
        status, body = get(url, args.timeout)
        ok = status == 200 and any(needle in body for needle in needles)
        print(f"[{'PASS' if ok else 'FAIL'}] {name} {url} -> {status}")
        if not ok:
            failed += 1
            if status != 200:
                print(f"       body: {body[:200]}")

    if failed:
        print(f"\n{failed} check(s) failed.")
        sys.exit(1)
    print("\nAll smoke checks passed.")


if __name__ == "__main__":
    main()
