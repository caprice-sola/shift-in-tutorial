"""CI gate for SLI 1 (docs/slis.md): p95 server time to answer GET /{code} < 50 ms.

Starts a real uvicorn process, creates one link, follows it FOLLOWS times over a
single keep-alive connection and checks the nearest-rank p95. The time is
measured at the client around each request, so it includes loopback and
client overhead: it is an upper bound on the server's own time.
"""

import http.client
import json
import math
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
P95_SLO_MS = 50  # docs/slis.md, SLI 1: p95 < 50 ms
FOLLOWS = 200
WARMUP = 10  # not counted: lets the process finish importing and open its connection


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def server():
    port = free_port()
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn", "snip.main:app",
            "--app-dir", "src", "--port", str(port), "--log-level", "warning",
        ],
        cwd=ROOT,
    )
    try:
        deadline = time.monotonic() + 15
        while True:
            try:
                socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
                break
            except OSError:
                if proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError("uvicorn did not start")
                time.sleep(0.1)
        yield port
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def p95(samples):
    """Nearest-rank 95th percentile."""
    ordered = sorted(samples)
    return ordered[math.ceil(0.95 * len(ordered)) - 1]


def test_redirect_p95_is_under_the_slo(server, capsys):
    conn = http.client.HTTPConnection("127.0.0.1", server)
    conn.request(
        "POST", "/api/links",
        body=json.dumps({"url": "https://example.com/latency"}),
        headers={"content-type": "application/json"},
    )
    created = conn.getresponse()
    assert created.status == 201
    code = json.loads(created.read())["code"]

    timings_ms = []
    for i in range(WARMUP + FOLLOWS):
        start = time.perf_counter()
        conn.request("GET", f"/{code}")
        response = conn.getresponse()
        response.read()
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert response.status == 307
        if i >= WARMUP:
            timings_ms.append(elapsed_ms)
    conn.close()

    measured = p95(timings_ms)
    with capsys.disabled():
        print(
            f"\nredirect latency over {len(timings_ms)} follows: "
            f"p95={measured:.2f} ms (SLO < {P95_SLO_MS} ms, margin {P95_SLO_MS - measured:.2f} ms), "
            f"median={sorted(timings_ms)[len(timings_ms) // 2]:.2f} ms, max={max(timings_ms):.2f} ms"
        )
    assert measured < P95_SLO_MS
