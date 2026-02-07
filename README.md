# Talk Python CLI

[![PyPI version](https://badge.fury.io/py/talk-python-cli.svg)](https://pypi.org/project/talk-python-cli/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

Unlock 500+ episodes of [Talk Python to Me](https://talkpython.fm), full transcripts, guest profiles, and 50+ [Talk Python Training](https://training.talkpython.fm) courses — all from your terminal. Search, browse, and pipe structured data into your scripts, AI agents, or automation workflows.

## Why use this?

- **Automation** — Query episode data, guest info, and course catalogs from scripts and pipelines.
- **LLM & AI integration** — Pipe JSON or Markdown output directly into AI agents, RAG systems, or chat workflows. Feed transcripts into RAG pipelines, build podcast assistants, or enrich your AI tools with real Python community knowledge.
- **Quick lookups** — Search episodes, pull transcripts, and browse courses without leaving the terminal.

## Installation

Requires Python 3.12+.

```bash
# Install it permanently with uv
uv tool install talk-python-cli

# Or try it instantly with uvx (no install needed)
uvx --from talk-python-cli talkpython episodes recent

# Or with pip
pip install talk-python-cli
```

This installs the `talkpython` command.

## Quick start

Copy this whole block and paste it into your terminal to see what you get.

```bash
# Search for episodes about FastAPI
talkpython episodes search "FastAPI"

# Get full details for a specific episode
talkpython episodes get 535

# Pull the transcript for an episode
talkpython episodes transcript 535

# List recent episodes
talkpython episodes recent --limit 5

# Search for a guest
talkpython guests search "Hynek"

# Browse all training courses
talkpython courses list
```

## Commands

### Episodes

| Command | Description |
|---------|-------------|
| `talkpython episodes search <query> [--limit N]` | Search episodes by keyword (default limit: 10) |
| `talkpython episodes get <show_id>` | Get full details for an episode |
| `talkpython episodes list` | List all episodes |
| `talkpython episodes recent [--limit N]` | Get the most recent episodes |
| `talkpython episodes transcript <show_id>` | Get the plain-text transcript |
| `talkpython episodes transcript-vtt <show_id>` | Get the WebVTT transcript (with timestamps) |

### Guests

| Command | Description |
|---------|-------------|
| `talkpython guests search <query> [--limit N]` | Search guests by name |
| `talkpython guests get <guest_id>` | Get details for a specific guest |
| `talkpython guests list` | List all guests, sorted by number of appearances |

### Courses

| Command | Description |
|---------|-------------|
| `talkpython courses search <query> [--course_id N]` | Search courses, chapters, and lectures |
| `talkpython courses get <course_id>` | Get full course details including chapters and lectures |
| `talkpython courses list` | List all available training courses |

## Output formats

The CLI auto-detects the best output format:

- **Interactive terminal** — Rich-formatted Markdown with styled panels and color.
- **Piped / redirected** — Compact JSON, ready for processing.

Override the default with `--format`:

```bash
# Force JSON output in the terminal
talkpython --format json episodes search "async"

# Force rich text output even when piping
talkpython --format text episodes recent | less -R
```

## Piping JSON to other tools

Because the CLI outputs JSON automatically when piped, it integrates naturally with tools like `jq`, `llm`, or your own scripts:

```bash
# Extract episode titles with jq
talkpython episodes search "testing" | jq '.title'

# Feed episode data into an LLM
talkpython episodes get 535 | llm "Summarize this podcast episode"

# Grab a transcript for RAG ingestion
talkpython episodes transcript 535 | your-rag-pipeline ingest
```

## Global options

| Option | Description |
|--------|-------------|
| `--format text\|json` | Force output format (auto-detected by default) |
| `--url <mcp-url>` | Override the MCP server URL (default: `https://talkpython.fm/api/mcp`) |
| `--version`, `-V` | Show version |

## Part of the Talk Python ecosystem

Talk Python CLI is one way to tap into the data behind the [Talk Python to Me](https://talkpython.fm) podcast and [Talk Python Training](https://training.talkpython.fm) courses. It connects to the same public [MCP server](https://talkpython.fm/api/mcp) that powers Talk Python's AI integrations — so whether you're building an agent, a search tool, or just want quick answers from the terminal, you're working with the real data.

- [Talk Python to Me Podcast](https://talkpython.fm)
- [Talk Python Training](https://training.talkpython.fm)

## License

MIT
