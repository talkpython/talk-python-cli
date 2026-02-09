"""Root Cyclopts application with global options."""

from __future__ import annotations

import json
import sys
import time
from typing import Annotated, Literal

import cyclopts
import httpx

from talk_python_cli import __version__
from talk_python_cli.client import DEFAULT_URL, MCPClient
from talk_python_cli.formatting import console, display_json, print_error

# ── Shared state ─────────────────────────────────────────────────────────────
# The meta-app handler stores the client here so command modules can access it.
_client: MCPClient | None = None


def get_client() -> MCPClient:
    """Return the active MCPClient (set by the meta-app launcher)."""
    assert _client is not None, 'MCPClient not initialised — this is a bug'
    return _client


# ── Root app ─────────────────────────────────────────────────────────────────
app = cyclopts.App(
    name='talkpython',
    help='CLI for the Talk Python to Me podcast and courses.\n\n'
    'Query episodes, guests, transcripts, and training courses\n'
    'from the Talk Python MCP server.',
    version=__version__,
    version_flags=['--version', '-V'],
)

# ── Register sub-apps (imported here to avoid circular imports) ──────────────
from talk_python_cli.courses import courses_app  # noqa: E402
from talk_python_cli.episodes import episodes_app  # noqa: E402
from talk_python_cli.guests import guests_app  # noqa: E402

app.command(episodes_app)
app.command(guests_app)
app.command(courses_app)


@app.command
def status() -> None:
    """Check whether the Talk Python MCP server is up and display its version info."""
    base = _client.base_url if _client else DEFAULT_URL
    t0 = time.monotonic()
    try:
        resp = httpx.get(base, timeout=15.0)
        elapsed_ms = (time.monotonic() - t0) * 1000
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as exc:
        elapsed_ms = (time.monotonic() - t0) * 1000
        console.print(f'[tp.error]STATUS: FAILED ({elapsed_ms:.2f} ms)[/tp.error]')
        console.print(f'[red]{exc}[/red]')
        sys.exit(1)

    # If piped / --format json, emit raw JSON
    if _client and _client.output_format == 'json':
        data['status'] = 'SUCCESS'
        data['response_ms'] = round(elapsed_ms, 2)
        display_json(json.dumps(data))
        return

    console.print()
    console.print(f'[tp.success]STATUS: SUCCESS[/tp.success] [tp.dim]({elapsed_ms:.2f} ms)[/tp.dim]')
    console.print()
    for key in ('name', 'version', 'description', 'documentation'):
        if key in data:
            console.print(f'[tp.label]{key}:[/tp.label] {data[key]}')
    console.print()


# ── Meta-app: handles global options before dispatching to sub-commands ──────
@app.meta.default
def launcher(
    *tokens: Annotated[str, cyclopts.Parameter(show=False, allow_leading_hyphen=True)],
    format: Annotated[
        Literal['text', 'json', 'markdown'],
        cyclopts.Parameter(
            name='--format',
            help="Output format: 'text' (rich Markdown), 'json', or 'markdown' (raw).",
        ),
    ] = 'text',
    url: Annotated[
        str,
        cyclopts.Parameter(
            name='--url',
            help='MCP server URL.',
            show_default=True,
        ),
    ] = DEFAULT_URL,
) -> None:
    global _client

    _client = MCPClient(base_url=url, output_format=format)
    try:
        app(tokens)
    except Exception as exc:
        print_error(str(exc))
        sys.exit(1)
    finally:
        _client.close()
        _client = None


# ── Entrypoint ───────────────────────────────────────────────────────────────
def main() -> None:
    """CLI entrypoint — called by the ``talkpython`` console script."""
    try:
        app.meta()
    except SystemExit:
        raise
    except Exception as exc:
        print_error(str(exc))
        sys.exit(1)
