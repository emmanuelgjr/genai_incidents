"""Pytest setup: make scripts/ importable as a top-level package."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slow: multi-minute scratch-repo builds (tests/test_oecd_stage1_freeze.py, "
        "~400 s). Runs by default, including in CI; developers may skip it "
        "locally with `pytest -m 'not slow'`.",
    )
    config.addinivalue_line(
        "markers",
        "real_robots: exercise ingest.common's real robots.txt logic "
        "instead of the autouse allow-everything stub below.",
    )
    config.addinivalue_line(
        "markers",
        "real_gate: run merge_and_dedupe._run_refresh_gate (D42/D67/D71 refresh gate) "
        "instead of the autouse no-op below.",
    )


@pytest.fixture(autouse=True)
def _ingest_common_test_safety(request, monkeypatch):
    """Every test gets a clean, network-free ingest.common:

    - the per-host rate-limit and robots.txt caches are reset, so no test
      can leak a real time.sleep() (or a poisoned robots verdict) into
      another test via shared module state;
    - robots.txt checks default to "allowed", so tests exercising
      robust_fetch()/conditional_fetch()'s retry mechanics (which mock
      urllib.request.urlopen directly) don't ALSO have that same mock
      intercept an internal robots.txt sub-fetch and short-circuit
      differently than they expect.

    Tests that specifically exercise the real robots.txt logic mark
    themselves ``@pytest.mark.real_robots`` to opt out of the stub.
    """
    import ingest.common as common

    common._reset_state_for_tests()
    if not request.node.get_closest_marker("real_robots"):
        monkeypatch.setattr(
            common, "robots_allowed",
            lambda url, min_interval=common.DEFAULT_MIN_INTERVAL: True,
        )
    yield
    common._reset_state_for_tests()


@pytest.fixture(autouse=True)
def _stub_refresh_gate(request, monkeypatch):
    """In-process tests that call merge_and_dedupe.main() build a from-scratch tmp
    corpus (DATA redirected) while the refresh gate reads the REAL repo's git HEAD
    baseline (D71/A3), so the two cannot be compared meaningfully. The gate has
    its own tests: unit tests on _check_refresh_merge_authorization /
    _load_gate_baseline (tests/test_d42_refresh_merge_gate.py), the wiring test
    marked ``real_gate``, and real subprocess builds in a scratch git repo
    (tests/test_oecd_stage1_freeze.py)."""
    if request.node.get_closest_marker("real_gate"):
        return
    import merge_and_dedupe as m

    monkeypatch.setattr(m, "_run_refresh_gate", lambda *a, **k: None)


class NetworkAccessAttempted(AssertionError):
    pass


@pytest.fixture(autouse=True)
def _no_real_network(monkeypatch):
    """D145: no in-process test may reach the real network. Name resolution and
    non-loopback connects raise NetworkAccessAttempted (an AssertionError that
    names the host), so a test that is silently networked fails loudly instead
    of depending on whatever upstream publishes today. Subprocess tests are
    separate processes and are unaffected."""
    import socket

    real_gai = socket.getaddrinfo
    real_connect = socket.socket.connect
    real_connect_ex = socket.socket.connect_ex
    loopback = {"localhost", "127.0.0.1", "::1", "", None}

    def gai(host, *a, **k):
        if host not in loopback:
            raise NetworkAccessAttempted(f"network access attempted: DNS lookup of {host!r}")
        return real_gai(host, *a, **k)

    def _guard(addr):
        if isinstance(addr, tuple) and addr and addr[0] not in loopback:
            raise NetworkAccessAttempted(f"network access attempted: connect to {addr!r}")

    def connect(self, addr):
        _guard(addr)
        return real_connect(self, addr)

    def connect_ex(self, addr):
        _guard(addr)
        return real_connect_ex(self, addr)

    monkeypatch.setattr(socket, "getaddrinfo", gai)
    monkeypatch.setattr(socket.socket, "connect", connect)
    monkeypatch.setattr(socket.socket, "connect_ex", connect_ex)
