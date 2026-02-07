# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-02-07

### Added
- `talkpython status` command to check MCP server health and display version info

### Changed
- Version is now read dynamically from package metadata via `importlib.metadata`
- Default output format is now always `text` (removed auto-detect that defaulted to `json` when piped)
- Development status upgraded from Alpha to Beta
- Added `readme` field to `pyproject.toml` so PyPI renders the README

---

## [0.1.0] - 2026-02-06

Initial release of the Talk Python CLI.

- Query podcast episodes by number or keyword
- Look up guest appearances
- Browse and search the Talk Python course catalog
- Rich terminal output with Markdown rendering
- JSON output mode via `--format json`
- Configurable MCP server URL via `--url`

---

## Template for Future Entries

<!--
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features or capabilities
- Files: `path/to/new/file.ext`, `another/file.ext`

### Changed
- Modifications to existing functionality
- Files: `path/to/modified/file.ext` (summary if many files)

### Deprecated
- Features that will be removed in future versions
- Files affected: `path/to/deprecated/file.ext`

### Removed
- Features or files that were deleted
- Files: `path/to/removed/file.ext`

### Fixed
- Bug fixes and corrections
- Files: `path/to/fixed/file.ext`

### Security
- Security patches or vulnerability fixes
- Files: `path/to/security/file.ext`

### Notes
- Additional context or important information
- Major dependencies updated
- Breaking changes explanation
-->
