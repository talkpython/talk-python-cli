"""Episode commands — search, get, list, recent, transcript."""

from __future__ import annotations

import cyclopts

from talk_python_cli.formatting import display

episodes_app = cyclopts.App(
    name='episodes',
    help='Browse and search Talk Python to Me podcast episodes.',
)


def _client():
    from talk_python_cli.app import get_client

    return get_client()


@episodes_app.command
def search(query: str, *, limit: int = 10) -> None:
    """Search episodes by keyword.

    Parameters
    ----------
    query
        Search keywords for episode titles and descriptions.
    limit
        Maximum number of results to return.
    """
    client = _client()
    args = {'query': query, 'limit': limit}
    content = client.call_tool('search_episodes', args)
    display(content, client.output_format)


@episodes_app.command
def get(show_id: int) -> None:
    """Get full details for an episode by its show ID.

    Parameters
    ----------
    show_id
        Episode show ID (e.g. 400).
    """
    client = _client()
    content = client.call_tool('get_episode', {'show_id': show_id})
    display(content, client.output_format)


@episodes_app.command(name='list')
def list_episodes() -> None:
    """List all podcast episodes with their show IDs and titles."""
    client = _client()
    content = client.call_tool('get_episodes')
    display(content, client.output_format)


@episodes_app.command
def recent(*, limit: int = 10) -> None:
    """Get the most recently published episodes.

    Parameters
    ----------
    limit
        Number of recent episodes to return.
    """
    client = _client()
    content = client.call_tool('get_recent_episodes', {'limit': limit})
    display(content, client.output_format)


@episodes_app.command
def transcript(show_id: int) -> None:
    """Get the full plain-text transcript for an episode.

    Parameters
    ----------
    show_id
        Episode show ID.
    """
    client = _client()
    content = client.call_tool('get_transcript_for_episode', {'show_id': show_id})
    display(content, client.output_format)


@episodes_app.command(name='transcript-vtt')
def transcript_vtt(show_id: int) -> None:
    """Get the transcript in WebVTT format (with timestamps).

    Parameters
    ----------
    show_id
        Episode show ID.
    """
    client = _client()
    content = client.call_tool('get_transcript_vtt', {'show_id': show_id})
    display(content, client.output_format)
