# Plan 001: Talk Python CLI — Standalone Package

## Context

The Talk Python MCP server at `https://talkpython.fm/api/mcp` exposes 12 tools for querying
podcast episodes, guests, transcripts, and courses via JSON-RPC 2.0. This project is a
**standalone, open-source CLI tool** (`talkpython`) that wraps those MCP tools as terminal
commands.

Full server documentation (tool names, parameters, descriptions):
**https://talkpython.fm/api/mcp/docs**

The package will be published to PyPI as `talk-python-cli` with the command name `talkpython`.

### MCP server tools (reference)

The server (v1.3.0) is public, read-only, no authentication required. Transport: Streamable HTTP.

| CLI command                      | MCP tool name              | Parameters                              |
|----------------------------------|----------------------------|-----------------------------------------|
| `episodes search`                | `search_episodes`          | `query` (str), `limit` (int, optional)  |
| `episodes get`                   | `get_episode`              | `show_id` (int)                         |
| `episodes list`                  | `get_episodes`             | *(none)*                                |
| `episodes recent`                | `get_recent_episodes`      | `limit` (int, optional)                 |
| `episodes transcript`            | `get_transcript_for_episode` | `show_id` (int)                       |
| `episodes transcript-vtt`        | `get_transcript_vtt`       | `show_id` (int)                         |
| `guests search`                  | `search_guests`            | `query` (str), `limit` (int, optional)  |
| `guests get`                     | `get_guest_by_id`          | `guest_id` (int)                        |
| `guests list`                    | `get_guests`               | *(none)*                                |
| `courses search`                 | `search_courses`           | `query` (str), `course_id` (int, opt.)  |
| `courses get`                    | `get_course_details`       | `course_id` (int)                       |
| `courses list`                   | `get_courses`              | *(none)*                                |

### Server-side prerequisite

The MCP server needs `?format=json` query parameter support so the CLI can receive structured
data instead of pre-formatted Markdown. That change lives in the main Talk Python web app repo
(not this one) and must be deployed before the CLI's `--format json` and auto-JSON-on-pipe
features work. The CLI should:

- Default to requesting `format=text` (works with the server today)
- Support `--format json` for when the server-side change is deployed
- Degrade gracefully if the server ignores the format parameter

## Project structure

Package lives at the repo root (not nested in a subdirectory):

Managed with **uv** — no manual venv creation, use `uv run`, `uv sync`, `uv lock`, etc.

```
talk-python-cli/
├── pyproject.toml
├── uv.lock                        # Committed to version control
├── LICENSE
├── README.md
├── .gitignore
├── src/
│   └── talk_python_cli/
│       ├── __init__.py         # Version string
│       ├── __main__.py         # python -m talk_python_cli support
│       ├── app.py              # Root Cyclopts app + global options
│       ├── client.py           # MCP HTTP client (httpx JSON-RPC wrapper)
│       ├── formatting.py       # Output formatting (rich Markdown or JSON)
│       ├── episodes.py         # Episode commands sub-app
│       ├── guests.py           # Guest commands sub-app
│       └── courses.py          # Course commands sub-app
└── tests/
    ├── __init__.py
    ├── conftest.py             # Shared fixtures (mock MCP responses)
    ├── test_client.py          # MCPClient unit tests
    ├── test_episodes.py        # Episode command tests
    ├── test_guests.py          # Guest command tests
    └── test_courses.py         # Course command tests
```

## Dependencies (pyproject.toml)

Created via `uv init`, then `uv add cyclopts httpx rich` and `uv add --dev pytest pytest-httpx`.

```toml
[project]
name = "talk-python-cli"
version = "0.1.0"
description = "CLI for the Talk Python to Me podcast and courses"
requires-python = ">=3.12"
license = "MIT"
authors = [
    { name = "Michael Kennedy", email = "michael@talkpython.fm" },
]
dependencies = [
    "cyclopts>=3.0",
    "httpx>=0.27",
    "rich>=13.0",
]

[project.scripts]
talkpython = "talk_python_cli.app:main"

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-httpx>=0.34",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

The `uv.lock` file is committed for reproducible installs.

## CLI commands

```
talkpython [--format text|json] [--url URL]

talkpython episodes search QUERY [--limit N]
talkpython episodes get SHOW_ID
talkpython episodes list
talkpython episodes recent [--limit N]
talkpython episodes transcript SHOW_ID
talkpython episodes transcript-vtt SHOW_ID

talkpython guests search QUERY [--limit N]
talkpython guests get GUEST_ID
talkpython guests list

talkpython courses search QUERY [--course-id ID]
talkpython courses get COURSE_ID
talkpython courses list
```

Global option `--format` defaults to `text` (rendered Markdown) but can be set to `json`
for machine-readable output. `--url` defaults to `https://talkpython.fm/api/mcp`.

### Auto-detection for piped output

When stdout is not a TTY (piped to another command), default to JSON format
for scripting convenience: `talkpython episodes recent | jq '.[]'`

## Key module designs

**`client.py`** — Thin wrapper around httpx making JSON-RPC calls:
```python
class MCPClient:
    def __init__(self, base_url: str, output_format: str = 'text'):
        self.base_url = base_url
        self.output_format = output_format
        self._msg_id = 0

    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        # POST to base_url?format={output_format}
        # JSON-RPC 2.0 envelope: {"jsonrpc":"2.0","id":N,"method":"tools/call","params":{...}}
        # Returns the result content text
```

**`formatting.py`** — Handles display:
- `text` format: render Markdown from server using rich
- `json` format: print with optional pretty-printing

**`app.py`** — Root app with global params:
```python
app = cyclopts.App(name='talkpython', help='Talk Python to Me CLI')
# Register sub-apps
app.command(episodes_app)
app.command(guests_app)
app.command(courses_app)
```

**`episodes.py`**, **`guests.py`**, **`courses.py`** — Each defines a sub-app:
```python
episodes_app = cyclopts.App(name='episodes', help='Podcast episode commands')

@episodes_app.command
def search(query: str, *, limit: int = 10):
    ...
```

## Implementation order

1. `uv init` — create `pyproject.toml`, then add dependencies with `uv add`
2. Implement `client.py` (HTTP JSON-RPC client)
3. Implement `formatting.py` (output rendering)
4. Implement `app.py` + command modules (`episodes.py`, `guests.py`, `courses.py`)
5. Add `__main__.py` for `python -m` support
6. Add tests with mocked HTTP responses (`uv add --dev pytest pytest-httpx`)
7. Verify against live server

## Verification

1. **Sync**: `uv sync` (installs all deps including dev group)
2. **Unit tests**: `uv run pytest tests/ -v`
3. **Smoke test**: `uv run talkpython episodes recent --limit 3`
4. **JSON output**: `uv run talkpython --format json episodes recent --limit 3`
5. **Piped output**: `uv run talkpython episodes recent | head` — should auto-detect JSON format
6. **Module entry**: `uv run python -m talk_python_cli episodes recent --limit 3`
