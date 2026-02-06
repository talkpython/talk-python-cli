"""Shared fixtures for Talk Python CLI tests."""

from __future__ import annotations

import json
from collections.abc import Generator

import httpx
import pytest
from pytest_httpx import HTTPXMock

from talk_python_cli.client import DEFAULT_URL, MCPClient


def request_json(req: httpx.Request) -> dict:
    """Parse the JSON body from a captured httpx request."""
    return json.loads(req.content)


# ── MCP JSON-RPC response helpers ────────────────────────────────────────────


def jsonrpc_result(id: int, result: dict) -> dict:
    """Build a JSON-RPC 2.0 success response."""
    return {'jsonrpc': '2.0', 'id': id, 'result': result}


def jsonrpc_error(id: int, code: int, message: str) -> dict:
    """Build a JSON-RPC 2.0 error response."""
    return {'jsonrpc': '2.0', 'id': id, 'error': {'code': code, 'message': message}}


def tool_result(id: int, text: str) -> dict:
    """Build a tools/call result with a single text content block."""
    return jsonrpc_result(id, {'content': [{'type': 'text', 'text': text}]})


def add_init_responses(httpx_mock: HTTPXMock, session_id: str = 'test-session') -> None:
    """Register the two responses required for the MCP initialize handshake.

    1. ``initialize`` request → JSON-RPC result with server capabilities
    2. ``notifications/initialized`` notification → 202 Accepted (no body)
    """
    # Response to "initialize" (id=1)
    httpx_mock.add_response(
        method='POST',
        url=DEFAULT_URL,
        json=jsonrpc_result(
            1,
            {
                'protocolVersion': '2025-03-26',
                'capabilities': {'tools': {}},
                'serverInfo': {'name': 'talkpython-mcp', 'version': '1.3.0'},
            },
        ),
        headers={'mcp-session-id': session_id},
    )
    # Response to "notifications/initialized" (no id → 202)
    httpx_mock.add_response(
        method='POST',
        url=DEFAULT_URL,
        status_code=202,
        headers={'mcp-session-id': session_id},
    )


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def mcp_client() -> Generator[MCPClient]:
    """Return a fresh MCPClient pointing at the default URL."""
    client = MCPClient(base_url=DEFAULT_URL, output_format='text')
    yield client
    client.close()


# ── Sample response data ─────────────────────────────────────────────────────

RECENT_EPISODES_TEXT = (
    'Recent Episodes (3 shown):\n\n'
    '535. PyView: Real-time Python Web Apps\n'
    '   Published: Jan 23, 2026\n'
    '   URL: https://talkpython.fm/episodes/show/535\n\n'
    '534. diskcache: Your secret Python perf weapon\n'
    '   Published: Jan 12, 2026\n'
    '   URL: https://talkpython.fm/episodes/show/534\n\n'
    '533. Web Frameworks in Prod by Their Creators\n'
    '   Published: Jan 05, 2026\n'
    '   URL: https://talkpython.fm/episodes/show/533'
)

SEARCH_EPISODES_TEXT = (
    'Found 2 episode(s) matching "FastAPI":\n\n'
    '- Episode 535: PyView: Real-time Python Web Apps\n'
    '  URL: https://talkpython.fm/episodes/show/535\n\n'
    '- Episode 533: Web Frameworks in Prod by Their Creators\n'
    '  URL: https://talkpython.fm/episodes/show/533'
)

EPISODE_DETAIL_TEXT = (
    'Episode 535: PyView: Real-time Python Web Apps\n\n'
    'Published: January 23, 2026\n'
    'Duration: 01:07:56\n'
    'URL: https://talkpython.fm/episodes/show/535\n\n'
    'Description:\nBuilding on the web is like working with the perfect clay.'
)

EPISODES_LIST_TEXT = (
    'All Episodes:\n'
    '535 - PyView: Real-time Python Web Apps\n'
    '534 - diskcache: Your secret Python perf weapon\n'
    '533 - Web Frameworks in Prod by Their Creators'
)

TRANSCRIPT_TEXT = 'Hello and welcome to Talk Python To Me, a weekly podcast on Python and related technologies.'

TRANSCRIPT_VTT_TEXT = 'WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nHello and welcome to Talk Python To Me.'

SEARCH_GUESTS_TEXT = 'Found 1 guest(s) matching "Hynek":\n\n- Hynek Schlawack (ID: 312)'

GUEST_DETAIL_TEXT = 'Hynek Schlawack\nGuest ID: 312\n\nBio:\nInfrastructure and software engineer from Berlin.'

GUESTS_LIST_TEXT = 'All Guests:\nHynek Schlawack (ID: 312) — 5 appearances\nGuido van Rossum (ID: 1) — 4 appearances'

SEARCH_COURSES_TEXT = (
    'Found 2 course(s) matching "Python":\n\n'
    '- Course 57: Just Enough Python for Data Scientists\n'
    '- Course 58: Agentic AI Programming for Python'
)

COURSE_DETAIL_TEXT = (
    'Course 57: Just Enough Python for Data Scientists\n\n'
    'Price: $29\nPublished: 2025-08-08\n'
    'URL: https://training.talkpython.fm/courses/just-enough-python'
)

COURSES_LIST_TEXT = (
    'Talk Python Training Courses (52 total):\n\n'
    '## Just Enough Python for Data Scientists\n'
    '   ID: 57 | Price: $29\n\n'
    '## Agentic AI Programming for Python\n'
    '   ID: 58 | Price: $39'
)
