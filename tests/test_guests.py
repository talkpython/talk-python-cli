"""Tests for guest commands."""

from __future__ import annotations

from pytest_httpx import HTTPXMock

from talk_python_cli.client import DEFAULT_URL
from tests.conftest import (
    GUEST_DETAIL_TEXT,
    GUESTS_LIST_TEXT,
    SEARCH_GUESTS_TEXT,
    add_init_responses,
    request_json,
    tool_result,
)


def _setup_tool_call(httpx_mock: HTTPXMock, text: str) -> None:
    add_init_responses(httpx_mock)
    httpx_mock.add_response(
        method='POST',
        url=DEFAULT_URL,
        json=tool_result(3, text),
    )


class TestGuestSearch:
    def test_search_sends_correct_params(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, SEARCH_GUESTS_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        client.call_tool('search_guests', {'query': 'Hynek', 'limit': 5})
        client.close()

        body = request_json(httpx_mock.get_requests()[-1])
        assert body['params']['name'] == 'search_guests'
        assert body['params']['arguments']['query'] == 'Hynek'
        assert body['params']['arguments']['limit'] == 5

    def test_search_returns_results(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, SEARCH_GUESTS_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        result = client.call_tool('search_guests', {'query': 'Hynek', 'limit': 10})
        client.close()

        assert 'Hynek Schlawack' in result
        assert '312' in result


class TestGuestGet:
    def test_get_sends_guest_id(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, GUEST_DETAIL_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        result = client.call_tool('get_guest_by_id', {'guest_id': 312})
        client.close()

        body = request_json(httpx_mock.get_requests()[-1])
        assert body['params']['arguments']['guest_id'] == 312
        assert 'Hynek Schlawack' in result

    def test_get_includes_bio(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, GUEST_DETAIL_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        result = client.call_tool('get_guest_by_id', {'guest_id': 312})
        client.close()

        assert 'Infrastructure and software engineer' in result


class TestGuestList:
    def test_list_sends_no_arguments(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, GUESTS_LIST_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        result = client.call_tool('get_guests')
        client.close()

        body = request_json(httpx_mock.get_requests()[-1])
        assert body['params']['name'] == 'get_guests'
        assert body['params']['arguments'] == {}
        assert 'Hynek Schlawack' in result
        assert 'Guido van Rossum' in result
