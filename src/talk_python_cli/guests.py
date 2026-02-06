"""Guest commands — search, get, list."""

from __future__ import annotations

import cyclopts

from talk_python_cli.formatting import display

guests_app = cyclopts.App(
    name='guests',
    help='Browse and search Talk Python to Me podcast guests.',
)


def _client():
    from talk_python_cli.app import get_client

    return get_client()


@guests_app.command
def search(query: str, *, limit: int = 10) -> None:
    """Search guests by name.

    Parameters
    ----------
    query
        Guest name or partial name to search for.
    limit
        Maximum number of results to return.
    """
    client = _client()
    content = client.call_tool('search_guests', {'query': query, 'limit': limit})
    display(content, client.output_format)


@guests_app.command
def get(guest_id: int) -> None:
    """Get detailed info about a guest by their ID.

    Parameters
    ----------
    guest_id
        The guest ID.
    """
    client = _client()
    content = client.call_tool('get_guest_by_id', {'guest_id': guest_id})
    display(content, client.output_format)


@guests_app.command(name='list')
def list_guests() -> None:
    """List all podcast guests, sorted by number of appearances."""
    client = _client()
    content = client.call_tool('get_guests')
    display(content, client.output_format)
