import pytest

from jinja2_indent.extension import reindent


def run(lines, current_indent, target_indent):
    """Helper: run reindent over a list of lines and return a list."""
    return list(reindent(lines, current_indent, target_indent))


class TestReindentBasics:
    def test_no_change_when_indents_equal(self):
        assert run(["    a\n", "    b\n"], 4, 4) == ["    a\n", "    b\n"]

    def test_increase_indent(self):
        assert run(["    a\n", "        b\n"], 4, 8) == ["        a\n", "            b\n"]

    def test_decrease_indent(self):
        assert run(["        a\n", "            b\n"], 8, 4) == ["    a\n", "        b\n"]

    def test_to_zero_indent(self):
        assert run(["    a\n", "        b\n"], 4, 0) == ["a\n", "    b\n"]

    def test_from_zero_indent(self):
        assert run(["a\n", "    b\n"], 0, 2) == ["  a\n", "      b\n"]

    def test_relative_offsets_preserved(self):
        lines = ["    a\n", "     b\n", "        c\n"]
        assert run(lines, 4, 10) == [
            "          a\n",
            "           b\n",
            "              c\n",
        ]

    def test_current_indent_zero(self):
        assert run(["a\n", "  b\n"], 0, 0) == ["a\n", "  b\n"]

    def test_line_exactly_at_current_indent(self):
        assert run(["    a\n"], 4, 4) == ["    a\n"]

    def test_tabs_inside_line_are_kept(self):
        # Tabs not at the start of the line are preserved.
        assert run(["    a\tb\n"], 4, 0) == ["a\tb\n"]


class TestReindentBlankLines:
    def test_blank_lines_stripped(self):
        assert run(["    a\n", "    \n", "\n", "    b\n"], 4, 8) == [
            "        a\n",
            "\n",
            "\n",
            "        b\n",
        ]

    def test_single_space_line_is_blank(self):
        assert run([" \n"], 0, 4) == ["\n"]

    def test_only_blank_lines(self):
        assert run(["   \n", " \t \n"], 0, 10) == ["\n", "\n"]

    def test_no_trailing_spaces_added_to_empty_lines(self):
        result = run(["    a\n", "\n"], 4, 20)
        assert result[1] == "\n"

    def test_lines_with_only_newline_characters(self):
        assert run(["\n", "\r\n"], 0, 5) == ["\n", "\r\n"]

    def test_blank_line_with_tab_does_not_raise(self):
        # A whitespace-only line with a tab is not treated as starting with a tab.
        assert run(["  \t  \n"], 0, 4) == ["\n"]


class TestReindentLineEndings:
    def test_preserves_lf(self):
        assert run(["    a\n"], 4, 0) == ["a\n"]

    def test_preserves_crlf(self):
        assert run(["    a\r\n"], 4, 0) == ["a\r\n"]

    def test_preserves_no_line_ending(self):
        assert run(["    a"], 4, 0) == ["a"]

    def test_preserves_mixed_endings(self):
        lines = ["    a\n", "    b\r\n", "    c"]
        assert run(lines, 4, 2) == ["  a\n", "  b\r\n", "  c"]


class TestReindentValidation:
    def test_negative_current_indent(self):
        with pytest.raises(ValueError, match="current_indent"):
            run(["a\n"], -1, 0)

    def test_negative_target_indent(self):
        with pytest.raises(ValueError, match="target_indent"):
            run(["a\n"], 0, -1)

    def test_leading_tab_raises(self):
        with pytest.raises(ValueError, match="tab"):
            run(["\ta\n"], 0, 0)

    def test_leading_spaces_then_tab_raises(self):
        with pytest.raises(ValueError, match="tab"):
            run(["    \ta\n"], 0, 0)

    def test_line_indented_less_than_current_indent_raises(self):
        with pytest.raises(ValueError, match="current_indent"):
            run(["  a\n"], 4, 0)


class TestReindentIterator:
    def test_empty_input(self):
        assert run([], 0, 4) == []

    def test_generator_returns_iterator(self):
        gen = reindent(["    a\n"], 4, 0)
        assert iter(gen) is gen

    def test_accepts_generator_input(self):
        def gen():
            yield "    a\n"
            yield "        b\n"

        assert list(reindent(gen(), 4, 0)) == ["a\n", "    b\n"]
