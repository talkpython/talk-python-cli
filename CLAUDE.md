# CLAUDE.md — Agent Instructions for talk-python-cli

## Project Overview

CLI client for the Talk Python to Me podcast and Talk Python Training courses.
Wraps a remote MCP server (`https://talkpython.fm/api/mcp`) using JSON-RPC 2.0
over HTTP. The CLI is a **thin client** — all business logic lives on the server.
The CLI handles argument parsing, HTTP transport, and output formatting.

Published on PyPI as `talk-python-cli`. Entry point: `talkpython`.

## Critical Rules

- **Use `uv pip install`, never `pip install`.**
- **Virtual environment is `./venv`, NOT `./.venv`.**
- **After every code edit, run: `ruff format && ruff check --fix`**
- **Use `pyrefly check` to validate type information after changes.**
- Do not add unnecessary abstractions, comments, or docstrings to unchanged code.

## Build & Run

```bash
# Activate venv
source venv/bin/activate

# Install in editable mode
uv pip install -e ".[dev]"

# Run CLI
talkpython --help
talkpython episodes search "fastapi"
talkpython status

# Run tests
pytest

# Lint & format (ALWAYS after edits)
ruff format && ruff check --fix

# Type check (ALWAYS after edits)
pyrefly check
```

## Project Structure

```
src/talk_python_cli/
  __init__.py       # Version from importlib.metadata
  __main__.py       # python -m entry point
  app.py            # Root Cyclopts app, global options, meta-handler, status cmd
  client.py         # MCPClient: httpx-based JSON-RPC 2.0 client
  formatting.py     # Rich output: Markdown panels (text) or JSON
  episodes.py       # Episode commands (search, get, list, recent, transcript)
  guests.py         # Guest commands (search, get, list)
  courses.py        # Course commands (search, get, list)

tests/
  conftest.py       # Shared fixtures, JSON-RPC response builders
  test_client.py    # MCPClient tests
  test_episodes.py  # Episode command tests
  test_guests.py    # Guest command tests
  test_courses.py   # Course command tests
```

## Architecture & Key Patterns

### CLI Framework: Cyclopts (not Click, not Typer)

- Root app in `app.py` with sub-apps for episodes, guests, courses.
- **Meta-app launcher** (`@app.meta.default`): intercepts all invocations to
  process global options (`--format`, `--url`) before dispatching to subcommands.
- Parameters use `Annotated[type, cyclopts.Parameter(...)]` for docs/defaults.
- Cyclopts auto-converts snake_case commands to kebab-case (e.g. `transcript_vtt` → `transcript-vtt`).

### Client Pattern

- `MCPClient` in `client.py` wraps httpx for JSON-RPC 2.0 over HTTP.
- Lazy initialization: `_ensure_initialized()` runs MCP handshake on first call.
- Session ID tracked via `Mcp-Session-Id` response header.
- `call_tool(tool_name, arguments)` is the only public API for MCP tool calls.
- Output format sent as URL query param: `?format=json` when JSON mode.
- No authentication required (public API).

### Lazy Client Access (avoids circular imports)

Each command module retrieves the client via a local helper:
```python
def _client():
    from talk_python_cli.app import get_client
    return get_client()
```
This deferred import avoids circular dependency since `app.py` imports the command modules.

### Output Formatting

- `display(content, format)` in `formatting.py` routes to markdown or JSON renderer.
- Text mode: Rich Markdown panel with "Talk Python" theme (cyan border, monokai code).
- JSON mode on TTY: pretty-printed with syntax highlighting.
- JSON mode piped: compact single-line JSON for scripting.

### Adding a New Command

1. Add function in the appropriate module (`episodes.py`, `guests.py`, `courses.py`).
2. Decorate with `@sub_app.default` or just define as a regular function in the sub-app.
3. Call `_client().call_tool('tool_name', {'arg': value})` to invoke the MCP tool.
4. Pass result to `display(result, _client().output_format)`.
5. Add tests in the corresponding test file using `pytest-httpx` mocks.

### Adding a New Command Group

1. Create `src/talk_python_cli/newgroup.py` with a `cyclopts.App(name='newgroup')`.
2. Register in `app.py`: `app.command(newgroup.sub_app)`.
3. Create `tests/test_newgroup.py`.

## Testing

- Framework: **pytest** with **pytest-httpx** for HTTP mocking.
- `conftest.py` provides helpers: `jsonrpc_result()`, `tool_result()`, `add_init_responses()`.
- Every test must call `add_init_responses(httpx_mock)` before making MCP client calls.
- Tests verify JSON-RPC request structure, argument passing, and response handling.

## Dependencies

| Package      | Purpose                        |
|-------------|--------------------------------|
| cyclopts    | CLI framework (commands, args) |
| httpx       | HTTP client for MCP calls      |
| rich        | Terminal output formatting      |
| pytest      | Testing (dev)                  |
| pytest-httpx| HTTP mocking in tests (dev)    |

Build system: **hatchling**. Package manager: **uv**.

## Config Files

- `pyproject.toml` — Package metadata, dependencies, entry points, build config
- `ruff.toml` — Line length 120, single quotes, target Python 3.14
- `pyrefly.toml` — Type checker config, search path includes `src/`
- `uv.lock` — Locked dependencies (committed)

## Style Conventions

- Line length: 120
- Quotes: single quotes
- Modern Python type syntax: `dict | None` not `Optional[dict]`
- `from __future__ import annotations` in all modules
- Private helpers prefixed with `_`
- Minimal docstrings: only on public functions/classes
- Python target: 3.12+ (currently targeting 3.14 in tooling)
