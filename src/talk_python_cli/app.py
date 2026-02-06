"""Root Cyclopts application with global options."""

from __future__ import annotations

import sys
from typing import Annotated, Literal

import cyclopts

from talk_python_cli import __version__
from talk_python_cli.client import DEFAULT_URL, MCPClient
from talk_python_cli.formatting import is_tty, print_error

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


# ── Meta-app: handles global options before dispatching to sub-commands ──────
@app.meta.default
def launcher(
    *tokens: Annotated[str, cyclopts.Parameter(show=False, allow_leading_hyphen=True)],
    format: Annotated[
        Literal['text', 'json'],
        cyclopts.Parameter(
            name='--format',
            help="Output format: 'text' (rich Markdown) or 'json'. Defaults to 'json' when stdout is piped.",
        ),
    ] = None,  # type: ignore
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

    # Auto-detect: default to json when piped, text when interactive
    if format is None:
        format = 'text' if is_tty() else 'json'

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
