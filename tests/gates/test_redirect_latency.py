"""Performance gate for SLI 1 (Redirect latency), per docs/slis.md.

Not part of the unit/API/system pyramid: docs/test-strategy.md calls this
out as its own lane ("Performance check (SLI 1)... doesn't fit the
pyramid... not a pass/fail unit assertion") and, per docs/slis.md, not yet
wired into CI as a blocking gate — that's M3b. This file is that lane,
runnable on demand.

Starts a real uvicorn subprocess rather than FastAPI's in-process
TestClient, so requests travel a real loopback socket. What's measured is
therefore client-observed round-trip time, not a server-internal timer —
snip has no timing middleware to report its own processing time, and
adding one is out of scope for a test file. Loopback overhead is
sub-millisecond, so against a 50ms budget this is a close, if anything
slightly stricter, proxy for "server time".
"""

import socket
import statistics
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"
PYTHON = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable

# docs/slis.md, SLI 1: "p95 server time to answer GET /{code}" -> "< 50 ms".
# Use this value exactly. Do not relax it.
P95_LATENCY_SLO_MS = 50

FOLLOW_COUNT = 200
WARMUP_COUNT = 5


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_until_up(client: httpx.Client, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    last_error = None
    while time.monotonic() < deadline:
        try:
            if client.get("/openapi.json").status_code == 200:
                return
        except httpx.TransportError as exc:
            last_error = exc
        time.sleep(0.1)
    raise RuntimeError(f"uvicorn didn't come up within {timeout}s: {last_error}")


@pytest.fixture
def live_server():
    """Runs snip in a real uvicorn subprocess (not the in-process TestClient
    used in tests/api/) so latency reflects a real socket round trip."""
    port = _free_port()
    proc = subprocess.Popen(
        [
            PYTHON, "-m", "uvicorn", "snip.main:app",
            "--app-dir", "src",
            "--host", "127.0.0.1",
            "--port", str(port),
            "--log-level", "warning",
        ],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    client = httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=5.0)
    try:
        _wait_until_up(client)
        yield client
    finally:
        client.close()
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        if proc.returncode not in (0, -15):
            output = proc.stdout.read() if proc.stdout else ""
            print(f"uvicorn exited {proc.returncode}:\n{output}")


def test_redirect_p95_latency_meets_slo(live_server):
    client = live_server

    created = client.post("/api/links", json={"url": "https://example.com/target"})
    assert created.status_code == 201
    code = created.json()["code"]

    # Unmeasured warmup: the first requests after a fresh process start
    # absorb one-time costs (import caches, connection setup) that would
    # skew a sample this small. The ~200 that follow are what's measured.
    for _ in range(WARMUP_COUNT):
        client.get(f"/{code}", follow_redirects=False)

    latencies_ms = []
    for _ in range(FOLLOW_COUNT):
        start = time.perf_counter()
        response = client.get(f"/{code}", follow_redirects=False)
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert response.status_code == 307
        latencies_ms.append(elapsed_ms)

    p95_ms = statistics.quantiles(latencies_ms, n=100, method="inclusive")[94]

    # Printed unconditionally, pass or fail, so CI logs show the real
    # margin -- run with `pytest -s` (or `--capture=no`) to see it on a
    # pass too; pytest hides captured stdout for passing tests otherwise.
    print(
        f"\nredirect latency over {FOLLOW_COUNT} follows: "
        f"p50={statistics.median(latencies_ms):.2f}ms "
        f"p95={p95_ms:.2f}ms "
        f"max={max(latencies_ms):.2f}ms "
        f"(SLO: p95 < {P95_LATENCY_SLO_MS}ms, docs/slis.md SLI 1)"
    )

    assert p95_ms < P95_LATENCY_SLO_MS
