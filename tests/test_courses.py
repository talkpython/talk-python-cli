"""Tests for course commands."""

from __future__ import annotations

from pytest_httpx import HTTPXMock

from talk_python_cli.client import DEFAULT_URL
from tests.conftest import (
    COURSE_DETAIL_TEXT,
    COURSES_LIST_TEXT,
    SEARCH_COURSES_TEXT,
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


class TestCourseSearch:
    def test_search_sends_query(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, SEARCH_COURSES_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        client.call_tool('search_courses', {'query': 'Python'})
        client.close()

        body = request_json(httpx_mock.get_requests()[-1])
        assert body['params']['name'] == 'search_courses'
        assert body['params']['arguments']['query'] == 'Python'

    def test_search_with_course_id(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, SEARCH_COURSES_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        client.call_tool('search_courses', {'query': 'Python', 'course_id': 57})
        client.close()

        body = request_json(httpx_mock.get_requests()[-1])
        args = body['params']['arguments']
        assert args['query'] == 'Python'
        assert args['course_id'] == 57

    def test_search_returns_results(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, SEARCH_COURSES_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        result = client.call_tool('search_courses', {'query': 'Python'})
        client.close()

        assert 'Course 57' in result
        assert 'Course 58' in result


class TestCourseGet:
    def test_get_sends_course_id(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, COURSE_DETAIL_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        result = client.call_tool('get_course_details', {'course_id': 57})
        client.close()

        body = request_json(httpx_mock.get_requests()[-1])
        assert body['params']['arguments']['course_id'] == 57
        assert 'Course 57' in result

    def test_get_includes_details(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, COURSE_DETAIL_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        result = client.call_tool('get_course_details', {'course_id': 57})
        client.close()

        assert '$29' in result
        assert '2025-08-08' in result


class TestCourseList:
    def test_list_sends_no_arguments(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, COURSES_LIST_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        client.call_tool('get_courses')
        client.close()

        body = request_json(httpx_mock.get_requests()[-1])
        assert body['params']['name'] == 'get_courses'
        assert body['params']['arguments'] == {}

    def test_list_returns_courses(self, httpx_mock: HTTPXMock) -> None:
        _setup_tool_call(httpx_mock, COURSES_LIST_TEXT)

        from talk_python_cli.client import MCPClient

        client = MCPClient(base_url=DEFAULT_URL, output_format='text')
        result = client.call_tool('get_courses')
        client.close()

        assert '52 total' in result
        assert 'Just Enough Python' in result
        assert 'Agentic AI' in result
