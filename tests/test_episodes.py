"""Tests for episode commands."""

from __future__ import annotations

from pytest_httpx import HTTPXMock

from talk_python_cli.client import DEFAULT_URL
from tests.conftest import (
    EPISODE_DETAIL_TEXT,
    EPISODES_LIST_TEXT,
    RECENT_EPISODES_TEXT,
    SEARCH_EPISODES_TEXT,
    TRANSCRIPT_TEXT,
    TRANSCRIPT_VTT_TEXT,
    add_init_responses,
    request_json,
    tool_result,
)


def _setup_tool_call(httpx_mock: HTTPXMock, text: str) -> None:
    """Register init + one tool-call response."""
    add_init_responses(httpx_mock)
    httpx_mock.add_response(
        method='POST',
        url=DEFAULT_URL,
        json=tool_result(3, text),
    )


class TestEpisodeSearch:
    def test_search_sends_correct_tool_call(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, SEARCH_EPISODES_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        result = client.call_tool('search_episodes', {'query': 'FastAPI', 'limit': 5})
        client.close()

        body = request_json(httpx_mock.get_requests()[-1])
        assert body['method'] == 'tools/call'
        assert body['params']['name'] == 'search_episodes'
        assert body['params']['arguments']['query'] == 'FastAPI'
        assert body['params']['arguments']['limit'] == 5
        assert 'FastAPI' in result

    def test_search_returns_results(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, SEARCH_EPISODES_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        result = client.call_tool('search_episodes', {'query': 'FastAPI', 'limit': 10})
        client.close()

        assert 'Episode 535' in result
        assert 'Episode 533' in result


class TestEpisodeGet:
    def test_get_episode_sends_show_id(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, EPISODE_DETAIL_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        result = client.call_tool('get_episode', {'show_id': 535})
        client.close()

        body = request_json(httpx_mock.get_requests()[-1])
        assert body['params']['arguments']['show_id'] == 535
        assert 'Episode 535' in result
        assert 'January 23, 2026' in result

    def test_get_episode_includes_url(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, EPISODE_DETAIL_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        result = client.call_tool('get_episode', {'show_id': 535})
        client.close()

        assert 'https://talkpython.fm/episodes/show/535' in result


class TestEpisodeList:
    def test_list_sends_no_arguments(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, EPISODES_LIST_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        result = client.call_tool('get_episodes')
        client.close()

        body = request_json(httpx_mock.get_requests()[-1])
        assert body['params']['arguments'] == {}
        assert '535 - PyView' in result


class TestRecentEpisodes:
    def test_recent_sends_limit(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, RECENT_EPISODES_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        result = client.call_tool('get_recent_episodes', {'limit': 3})
        client.close()

        body = request_json(httpx_mock.get_requests()[-1])
        assert body['params']['arguments']['limit'] == 3
        assert '535.' in result
        assert '534.' in result
        assert '533.' in result


class TestTranscript:
    def test_transcript_returns_text(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, TRANSCRIPT_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        result = client.call_tool('get_transcript_for_episode', {'show_id': 535})
        client.close()

        assert 'Hello and welcome to Talk Python To Me' in result

    def test_transcript_vtt_returns_webvtt(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, TRANSCRIPT_VTT_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        result = client.call_tool('get_transcript_vtt', {'show_id': 535})
        client.close()

        assert result.startswith('WEBVTT')
        assert '00:00:00.000' in result
