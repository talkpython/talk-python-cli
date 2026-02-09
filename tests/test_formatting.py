"""Tests for output formatting."""

from __future__ import annotations

from talk_python_cli.formatting import display, display_markdown_raw


class TestDisplayMarkdownRaw:
    def test_prints_raw_content(self, capsys) -> None:
        display_markdown_raw('# Hello\n\nSome **bold** text')

        captured = capsys.readouterr()
        assert captured.out == '# Hello\n\nSome **bold** text\n'

    def test_no_rich_markup_in_output(self, capsys) -> None:
        display_markdown_raw('## Heading\n- item 1\n- item 2')

        captured = capsys.readouterr()
        # Raw markdown should appear verbatim — no Rich panel borders or styling
        assert '## Heading' in captured.out
        assert '- item 1' in captured.out
        assert '╭' not in captured.out  # no Rich panel border


class TestDisplayRouting:
    def test_markdown_format_routes_to_raw(self, capsys) -> None:
        display('# Raw markdown', 'markdown')

        captured = capsys.readouterr()
        assert captured.out == '# Raw markdown\n'

    def test_text_format_does_not_print_raw(self, capsys) -> None:
        display('# Rendered', 'text')

        captured = capsys.readouterr()
        # Text mode uses Rich console, so raw '# Rendered' should NOT appear verbatim
        # (Rich renders it as a heading without the # prefix)
        assert '# Rendered' not in captured.out
