"""Output formatting — Rich Markdown rendering and JSON display."""

from __future__ import annotations

import json
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

# ── Custom theme for Talk Python branding ────────────────────────────────────
_TALK_PYTHON_THEME = Theme(
    {
        'tp.title': 'bold cyan',
        'tp.heading': 'bold magenta',
        'tp.id': 'bold yellow',
        'tp.url': 'blue underline',
        'tp.date': 'green',
        'tp.dim': 'dim',
        'tp.error': 'bold red',
        'tp.success': 'bold green',
        'tp.label': 'bold white',
    }
)

console = Console(theme=_TALK_PYTHON_THEME, highlight=False)
error_console = Console(theme=_TALK_PYTHON_THEME, stderr=True, highlight=False)


def is_tty() -> bool:
    """Return True if stdout is connected to a terminal."""
    return sys.stdout.isatty()


def display(content: str, output_format: str) -> None:
    """Route content to the appropriate renderer."""
    if output_format == 'json':
        display_json(content)
    else:
        display_markdown(content)


def display_markdown(content: str) -> None:
    """Render Markdown content with Rich, wrapped in a styled panel."""
    md = Markdown(content, code_theme='monokai')

    panel = Panel(
        md,
        border_style='cyan',
        title='[bold cyan]Talk Python[/bold cyan]',
        title_align='left',
        padding=(1, 2),
    )
    console.print(panel)


def display_json(content: str) -> None:
    """Output JSON content — pretty-printed if on a TTY, raw otherwise."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError, TypeError:
        # Server may have returned Markdown even though JSON was requested;
        # fall back to printing the raw text.
        console.print(content)
        return

    if is_tty():
        from rich.syntax import Syntax

        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        syntax = Syntax(formatted, 'json', theme='monokai', word_wrap=True)
        console.print(syntax)
    else:
        # Raw compact JSON for piping
        print(json.dumps(data, ensure_ascii=False))


def print_error(message: str) -> None:
    """Print a styled error message to stderr."""
    error_console.print(
        Text.assemble(
            ('ERROR', 'bold red'),
            (' ', ''),
            (message, 'red'),
        )
    )


def print_info(message: str) -> None:
    """Print a styled informational message."""
    console.print(f'[tp.dim]{message}[/tp.dim]')
