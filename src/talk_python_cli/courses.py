"""Course commands — search, get, list."""

from __future__ import annotations

import cyclopts

from talk_python_cli.formatting import display

courses_app = cyclopts.App(
    name='courses',
    help='Browse and search Talk Python Training courses.',
)


def _client():
    from talk_python_cli.app import get_client

    return get_client()


@courses_app.command
def search(query: str, *, course_id: int | None = None) -> None:
    """Search courses, chapters, and lectures by keyword.

    Parameters
    ----------
    query
        Keywords for course, chapter, or lecture titles.
    course_id
        Limit search to a specific course (optional).
    """
    client = _client()
    args: dict = {'query': query}
    if course_id is not None:
        args['course_id'] = course_id
    content = client.call_tool('search_courses', args)
    display(content, client.output_format)


@courses_app.command
def get(course_id: int) -> None:
    """Get full details for a course by ID, including chapters and lectures.

    Parameters
    ----------
    course_id
        The course ID.
    """
    client = _client()
    content = client.call_tool('get_course_details', {'course_id': course_id})
    display(content, client.output_format)


@courses_app.command(name='list')
def list_courses() -> None:
    """List all available Talk Python Training courses."""
    client = _client()
    content = client.call_tool('get_courses')
    display(content, client.output_format)
