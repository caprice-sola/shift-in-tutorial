"""SLI 1 CI gate: redirect (GET /{code}) p95 latency must stay under 50ms
(docs/slis.md). Intentionally NOT a unit or API-layer test - it needs a real
running process to measure anything meaningful about latency, which is
exactly docs/test-strategy.md's bar for justifying a level above unit.

Measures client-side wall-clock latency over loopback (httpx), not
instrumented server-internal time - close enough for a workshop-scale gate,
but note the difference if you ever compare this number to real production
telemetry for the same SLI.

Also intentionally NOT part of the Stop hook's fast in-loop check (M3a) - CI
is where the app can afford a heavier, slower gate like this one. Run it
directly with `pytest tests/gates -q`.
"""
import subprocess
import sys
import time
from pathlib import Path

import httpx2 as httpx

HOST = "127.0.0.1"
PORT = 8931
BASE_URL = f"http://{HOST}:{PORT}"
P95_TARGET_MS = 50  # docs/slis.md SLI 1
SAMPLE_SIZE = 50
WARMUP_REQUESTS = 5
STARTUP_TIMEOUT_S = 10


def _wait_for_server(client: httpx.Client, proc: subprocess.Popen) -> None:
    deadline = time.monotonic() + STARTUP_TIMEOUT_S
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(
                f"uvicorn exited early (code {proc.returncode}) instead of starting - "
                f"port {PORT} may already be in use"
            )
        try:
            if client.get(f"{BASE_URL}/openapi.json").status_code == 200:
                return
        except httpx.ConnectError:
            pass
        time.sleep(0.1)
    raise RuntimeError("snip server didn't come up in time")


def test_redirect_p95_latency_under_sli_target():
    repo_root = Path(__file__).resolve().parents[2]
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "snip.main:app", "--app-dir", "src",
         "--host", HOST, "--port", str(PORT), "--log-level", "warning"],
        cwd=repo_root,
    )
    try:
        with httpx.Client() as client:
            _wait_for_server(client, proc)
            code = client.post(
                f"{BASE_URL}/api/links", json={"url": "https://example.com"}
            ).json()["code"]

            for _ in range(WARMUP_REQUESTS):
                client.get(f"{BASE_URL}/{code}", follow_redirects=False)

            durations_ms = []
            for _ in range(SAMPLE_SIZE):
                start = time.perf_counter()
                resp = client.get(f"{BASE_URL}/{code}", follow_redirects=False)
                durations_ms.append((time.perf_counter() - start) * 1000)
                assert resp.status_code == 307

            durations_ms.sort()
            p95 = durations_ms[int(len(durations_ms) * 0.95)]
            print(f"redirect p95 latency: {p95:.2f} ms over {SAMPLE_SIZE} requests "
                  f"(target: < {P95_TARGET_MS} ms)")
            assert p95 < P95_TARGET_MS, (
                f"SLI 1 violation: p95 redirect latency {p95:.2f}ms exceeds "
                f"the {P95_TARGET_MS}ms target (docs/slis.md)"
            )
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
