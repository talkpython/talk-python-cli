"""Tests for the MCP HTTP client."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from talk_python_cli.client import DEFAULT_URL, MCPClient, MCPError
from tests.conftest import (
    add_init_responses,
    jsonrpc_error,
    jsonrpc_result,
    request_json,
    tool_result,
)


class TestMCPClientInit:
    """Verify the MCP initialize handshake."""

    def test_initialize_sends_correct_requests(self, httpx_mock: HTTPXMock, mcp_client: MCPClient) -> None:
        add_init_responses(httpx_mock)
        httpx_mock.add_response(
            method='POST',
            url=DEFAULT_URL,
            json=tool_result(3, 'hello'),
        )

        mcp_client.call_tool('search_episodes', {'query': 'test'})

        requests = httpx_mock.get_requests()
        assert len(requests) == 3

        # First request: initialize
        init_body = request_json(requests[0])
        assert init_body['method'] == 'initialize'
        assert 'protocolVersion' in init_body['params']
        assert init_body['params']['clientInfo']['name'] == 'talk-python-cli'

        # Second request: notifications/initialized
        notif_body = request_json(requests[1])
        assert notif_body['method'] == 'notifications/initialized'
        assert 'id' not in notif_body  # notifications have no id

        # Third request: tools/call
        call_body = request_json(requests[2])
        assert call_body['method'] == 'tools/call'
        assert call_body['params']['name'] == 'search_episodes'

    def test_session_id_propagated(self, httpx_mock: HTTPXMock, mcp_client: MCPClient) -> None:
        add_init_responses(httpx_mock, session_id='session-abc')
        httpx_mock.add_response(
            method='POST',
            url=DEFAULT_URL,
            json=tool_result(3, 'ok'),
        )

        mcp_client.call_tool('get_episodes')

        # The tools/call request should carry the session header
        last_req = httpx_mock.get_requests()[-1]
        assert last_req.headers.get('mcp-session-id') == 'session-abc'

    def test_initialize_only_once(self, httpx_mock: HTTPXMock, mcp_client: MCPClient) -> None:
        add_init_responses(httpx_mock)
        httpx_mock.add_response(method='POST', url=DEFAULT_URL, json=tool_result(3, 'one'))
        httpx_mock.add_response(method='POST', url=DEFAULT_URL, json=tool_result(4, 'two'))

        mcp_client.call_tool('get_episodes')
        mcp_client.call_tool('get_guests')

        requests = httpx_mock.get_requests()
        # init (1) + notification (1) + two tool calls (2) = 4
        assert len(requests) == 4
        methods = [request_json(r)['method'] for r in requests]
        assert methods.count('initialize') == 1


class TestCallTool:
    """Verify tool call behaviour."""

    def test_returns_text_content(self, httpx_mock: HTTPXMock, mcp_client: MCPClient) -> None:
        add_init_responses(httpx_mock)
        httpx_mock.add_response(
            method='POST',
            url=DEFAULT_URL,
            json=tool_result(3, 'Episode 535: PyView'),
        )

        result = mcp_client.call_tool('get_episode', {'show_id': 535})
        assert result == 'Episode 535: PyView'

    def test_passes_arguments(self, httpx_mock: HTTPXMock, mcp_client: MCPClient) -> None:
        add_init_responses(httpx_mock)
        httpx_mock.add_response(
            method='POST',
            url=DEFAULT_URL,
            json=tool_result(3, 'results'),
        )

        mcp_client.call_tool('search_episodes', {'query': 'FastAPI', 'limit': 5})

        body = request_json(httpx_mock.get_requests()[-1])
        assert body['params']['arguments'] == {'query': 'FastAPI', 'limit': 5}

    def test_empty_arguments_sends_empty_dict(self, httpx_mock: HTTPXMock, mcp_client: MCPClient) -> None:
        add_init_responses(httpx_mock)
        httpx_mock.add_response(
            method='POST',
            url=DEFAULT_URL,
            json=tool_result(3, 'all episodes'),
        )

        mcp_client.call_tool('get_episodes')

        body = request_json(httpx_mock.get_requests()[-1])
        assert body['params']['arguments'] == {}

    def test_jsonrpc_error_raises(self, httpx_mock: HTTPXMock, mcp_client: MCPClient) -> None:
        add_init_responses(httpx_mock)
        httpx_mock.add_response(
            method='POST',
            url=DEFAULT_URL,
            json=jsonrpc_error(3, -32602, 'Invalid params'),
        )

        with pytest.raises(MCPError) as exc_info:
            mcp_client.call_tool('get_episode', {'show_id': -1})

        assert exc_info.value.code == -32602
        assert 'Invalid params' in str(exc_info.value)

    def test_multiple_content_blocks_joined(self, httpx_mock: HTTPXMock, mcp_client: MCPClient) -> None:
        add_init_responses(httpx_mock)
        httpx_mock.add_response(
            method='POST',
            url=DEFAULT_URL,
            json=jsonrpc_result(
                3,
                {
                    'content': [
                        {'type': 'text', 'text': 'Part 1'},
                        {'type': 'text', 'text': 'Part 2'},
                    ],
                },
            ),
        )

        result = mcp_client.call_tool('get_episode', {'show_id': 1})
        assert result == 'Part 1\nPart 2'


class TestOutputFormat:
    """Verify the format query parameter."""

    def test_text_format_no_query_param(self, httpx_mock: HTTPXMock) -> None:
        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        add_init_responses(httpx_mock)
        httpx_mock.add_response(
            method='POST',
            url=DEFAULT_URL,
            json=tool_result(3, 'text content'),
        )

        client.call_tool('get_episodes')
        # All requests should go to the base URL without ?format=
        for req in httpx_mock.get_requests():
            assert 'format=' not in str(req.url)
        client.close()

    def test_json_format_adds_query_param(self, httpx_mock: HTTPXMock) -> None:
        json_url = f'{DEFAULT_URL}?format=json'
        client = MCPClient(base_url=DEFAULT_URL, output_format='json')

        httpx_mock.add_response(
            method='POST',
            url=json_url,
            json=jsonrpc_result(
                1,
                {
                    'protocolVersion': '2025-03-26',
                    'capabilities': {'tools': {}},
                    'serverInfo': {'name': 'test', 'version': '0.1'},
                },
            ),
            headers={'mcp-session-id': 's1'},
        )
        httpx_mock.add_response(method='POST', url=json_url, status_code=202, headers={'mcp-session-id': 's1'})
        httpx_mock.add_response(
            method='POST',
            url=json_url,
            json=tool_result(3, '{"data": "json"}'),
        )

        client.call_tool('get_episodes')
        for req in httpx_mock.get_requests():
            assert 'format=json' in str(req.url)
        client.close()

    def test_markdown_format_adds_query_param(self, httpx_mock: HTTPXMock) -> None:
        md_url = f'{DEFAULT_URL}?format=markdown'
        client = MCPClient(base_url=DEFAULT_URL, output_format='markdown')

        httpx_mock.add_response(
            method='POST',
            url=md_url,
            json=jsonrpc_result(
                1,
                {
                    'protocolVersion': '2025-03-26',
                    'capabilities': {'tools': {}},
                    'serverInfo': {'name': 'test', 'version': '0.1'},
                },
            ),
            headers={'mcp-session-id': 's1'},
        )
        httpx_mock.add_response(method='POST', url=md_url, status_code=202, headers={'mcp-session-id': 's1'})
        httpx_mock.add_response(
            method='POST',
            url=md_url,
            json=tool_result(3, '# Episode 535\n\nSome markdown content'),
        )

        client.call_tool('get_episodes')
        for req in httpx_mock.get_requests():
            assert 'format=markdown' in str(req.url)
        client.close()


class TestContextManager:
    """Verify MCPClient works as a context manager."""

    def test_context_manager(self, httpx_mock: HTTPXMock) -> None:
        add_init_responses(httpx_mock)
        httpx_mock.add_response(
            method='POST',
            url=DEFAULT_URL,
            json=tool_result(3, 'ok'),
        )

        with MCPClient(base_url=DEFAULT_URL) as client:
            result = client.call_tool('get_episodes')
            assert result == 'ok'
