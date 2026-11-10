"""D145 guard (tests/conftest.py::_no_real_network): every in-process path that could
reach a non-loopback host must raise NetworkAccessAttempted, and loopback must still work.
The autouse fixture is active inside these tests, so they exercise the real patches.
Nothing here sends a packet off the machine: the guard raises before any syscall."""

from __future__ import annotations

import socket

import pytest

def blocked():
    """conftest.NetworkAccessAttempted is an AssertionError whose text names the attempt."""
    return pytest.raises(AssertionError, match="network access attempted")


# Unroutable documentation addresses: TEST-NET-1 (RFC 5737) and 2001:db8::/32 (RFC 3849),
# so a guard regression cannot send a packet to a real host.
REMOTE_V4 = "192.0.2.1"
REMOTE_V6 = "2001:db8::1"


def test_dns_lookup_of_remote_name_raises():
    with blocked():
        socket.getaddrinfo("example.invalid", 80)
    with blocked():
        socket.getaddrinfo(b"example.invalid", 80)


@pytest.mark.parametrize("host", ["localhost", "127.0.0.1", "127.0.0.2", "127.255.255.254", "::1", b"127.0.0.1", b"localhost"])
def test_loopback_hosts_resolve(host):
    assert socket.getaddrinfo(host, 80)


def test_connect_variants_to_remote_raise():
    s4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    s4.settimeout(1)
    s6.settimeout(1)  # bound the cost if a mutant lets a connect through
    try:
        with blocked():
            s4.connect((REMOTE_V4, 80))
        with blocked():
            s4.connect_ex((REMOTE_V4, 80))
        with blocked():
            s4.connect((REMOTE_V4.encode(), 80))  # bytes host
        with blocked():
            s6.connect((REMOTE_V6, 80, 0, 0))
        with blocked():
            s6.connect_ex((REMOTE_V6, 80, 0, 0))
    finally:
        s4.close()
        s6.close()


def test_create_connection_to_remote_raises():
    with blocked():
        socket.create_connection((REMOTE_V4, 80), timeout=1)
    with blocked():
        socket.create_connection(("example.invalid", 80), timeout=1)


def test_udp_sendto_and_sendmsg_to_remote_raise():
    u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    u6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    try:
        with blocked():
            u.sendto(b"x", (REMOTE_V4, 53))
        with blocked():
            u.sendto(b"x", 0, (REMOTE_V4, 53))  # the flags form
        with blocked():
            u.sendto(b"x", (REMOTE_V4.encode(), 53))
        with blocked():
            u6.sendto(b"x", (REMOTE_V6, 53, 0, 0))
        if hasattr(u, "sendmsg"):
            with blocked():
                u.sendmsg([b"x"], [], 0, (REMOTE_V4, 53))
    finally:
        u.close()
        u6.close()


def test_loopback_udp_roundtrip_still_works():
    rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        rx.bind(("127.0.0.1", 0))
        rx.settimeout(5)
        port = rx.getsockname()[1]
        tx.sendto(b"ping", ("127.0.0.1", port))
        assert rx.recvfrom(16)[0] == b"ping"
        tx.sendto(b"pong", ("localhost", port))
        assert rx.recvfrom(16)[0] == b"pong"
        tx.sendto(b"bytes", (b"127.0.0.1", port))
        assert rx.recvfrom(16)[0] == b"bytes"
    finally:
        rx.close()
        tx.close()


def test_loopback_tcp_connect_still_works():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        srv.bind(("127.0.0.1", 0))
        srv.listen(5)
        port = srv.getsockname()[1]
        c = socket.create_connection(("127.0.0.1", port), timeout=5)
        c.close()
        c2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        assert c2.connect_ex(("127.0.0.1", port)) == 0
        c2.close()
    finally:
        srv.close()


def test_whole_loopback_block_is_loopback_not_just_127_0_0_1():
    """127.0.0.2 is loopback: the guard must not raise NetworkAccessAttempted for it
    (the OS may still refuse the connection, which is a different error)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        try:
            s.connect(("127.0.0.2", 9))
        except AssertionError as e:
            assert "network access attempted" not in str(e), "127.0.0.2 was treated as non-loopback"
            raise
        except OSError:
            pass  # refused / timed out / unroutable: not the guard
    finally:
        s.close()
