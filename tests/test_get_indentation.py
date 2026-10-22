import pytest

from jinja2_indent.extension import get_indentation, indent_of


class TestIndentOf:
    def test_empty_line(self):
        assert indent_of("", 4) == 0

    def test_no_indentation(self):
        assert indent_of("hello", 4) == 0

    def test_spaces_only_prefix(self):
        assert indent_of("    hello", 4) == 4
        assert indent_of("  hello", 4) == 2

    def test_single_tab(self):
        assert indent_of("\thello", 4) == 4

    def test_two_tabs(self):
        assert indent_of("\t\thello", 4) == 8

    def test_tab_after_spaces(self):
        # one space, then a tab: 1 -> (4 - 1 % 4) = 3, total 4
        assert indent_of(" \thello", 4) == 4

    def test_spaces_after_tab(self):
        # tab (4), then 2 spaces -> 6
        assert indent_of("\t  hello", 4) == 6

    def test_mixed_indentation(self):
        # "  \t hello": 2 -> tab adds 4-2=2 -> 4, space -> 5
        assert indent_of("  \t hello", 4) == 5

    def test_custom_tab_size(self):
        assert indent_of("\thello", 8) == 8
        assert indent_of(" \thello", 8) == 8
        assert indent_of("\thello", 2) == 2

    def test_tab_size_three(self):
        # "  \t": 2 -> tab adds (3 - 2 % 3) = 1 -> 3
        assert indent_of("  \thello", 3) == 3
        # "\t\t": 3 + 3 = 6
        assert indent_of("\t\thello", 3) == 6

    def test_line_of_only_spaces(self):
        # the function does not filter lines itself — it just counts
        assert indent_of("     ", 4) == 5

    def test_line_of_only_tabs(self):
        assert indent_of("\t\t", 4) == 8

    def test_whitespace_only_line_no_nonws(self):
        assert indent_of("   \t   ", 4) == 7

    def test_indent_stops_at_first_non_ws(self):
        # after 'h' spaces and tabs are not counted
        assert indent_of("  hi\t\t", 4) == 2

    def test_unicode_non_ws(self):
        assert indent_of("  привет", 4) == 2

    def test_tab_at_start_tab_size_one(self):
        assert indent_of("\thello", 1) == 1

    def test_special_characters_in_content(self):
        assert indent_of("\n\t", 4) == 0  # \n is not a whitespace prefix, break immediately
        assert indent_of(" \n", 4) == 1  # space, then \n -> break


class TestGetIndentation:
    def test_empty_list(self):
        assert get_indentation([]) == 0

    def test_only_blank_lines(self):
        assert get_indentation(["\n", "   ", "\t\t", ""]) == 0

    def test_only_whitespace_lines(self):
        assert get_indentation(["   ", "\t", " \t "]) == 0

    def test_single_line_no_indent(self):
        assert get_indentation(["hello"]) == 0

    def test_single_line_indent(self):
        assert get_indentation(["    hello"]) == 4

    def test_minimum_across_lines(self):
        lines = [
            "        deep",  # 8
            "    medium",  # 4
            "  shallow",  # 2
        ]
        assert get_indentation(lines) == 2

    def test_blank_lines_ignored(self):
        lines = [
            "        deep",
            "",
            "   ",  # spaces only — ignored
            "    medium",
            "\t\t\t",  # tabs only — ignored
            "  shallow",
        ]
        assert get_indentation(lines) == 2

    def test_tabs_and_spaces_mixed(self):
        lines = [
            "\t\tcode",  # 8
            "  \tcode",  # 4 (2 + (4-2)=4)
            " \tcode",  # 4
        ]
        assert get_indentation(lines) == 4

    def test_custom_tab_size(self):
        lines = ["\tcode", "  code"]
        assert get_indentation(lines, tab_size=8) == 2
        assert get_indentation(lines, tab_size=4) == 2
        assert get_indentation(lines, tab_size=2) == 2
        assert get_indentation(lines, tab_size=1) == 1

    def test_custom_tab_size_affects_result(self):
        lines = ["\tcode"]
        assert get_indentation(lines, tab_size=2) == 2
        assert get_indentation(lines, tab_size=4) == 4
        assert get_indentation(lines, tab_size=8) == 8

    def test_iterator_input(self):
        lines = (line for line in ["    a", "  b", "      c"])
        assert get_indentation(lines) == 2

    def test_tuple_input(self):
        assert get_indentation(("    a", "  b")) == 2

    def test_generator_input(self):
        def gen():
            yield "      x"
            yield "  y"

        assert get_indentation(gen()) == 2

    def test_all_lines_zero_indent(self):
        assert get_indentation(["a", "b", "c"]) == 0

    def test_zero_indent_among_indented(self):
        lines = ["    code", "code", "  code"]
        assert get_indentation(lines) == 0

    def test_single_tab_line(self):
        assert get_indentation(["\tcode"]) == 4

    def test_tab_size_one(self):
        assert get_indentation(["\tcode", " code"], tab_size=1) == 1

    def test_whitespace_only_with_tabs_and_spaces(self):
        # all lines are empty according to strip() — result is 0
        lines = ["\t \t", "    ", "\t\t\t"]
        assert get_indentation(lines) == 0

    def test_lines_with_trailing_whitespace(self):
        lines = ["   code   ", "  code\t"]
        assert get_indentation(lines) == 2

    def test_crlf_style_lines(self):
        lines = ["    code\r\n", "  code\r\n"]
        # is \r considered a non-ws prefix after code? no, \r comes after code
        assert get_indentation(lines) == 2

    @pytest.mark.parametrize("tab_size", [0, -1, -4, -100])
    def test_non_positive_tab_size_raises(self, tab_size):
        with pytest.raises(ValueError, match="tab_size must be positive"):
            get_indentation(["  code"], tab_size=tab_size)

    def test_large_tab_size(self):
        lines = ["\tcode", "        code"]  # 100 and 8
        assert get_indentation(lines, tab_size=100) == 8

    def test_mixed_content_and_indent(self):
        lines = [
            "def foo():",
            "    return 1",
            "    ",
            "",
            "    pass",
        ]
        assert get_indentation(lines) == 0

    def test_deep_nesting(self):
        lines = [
            "            deepest",  # 12
            "        mid",  # 8
            "    top",  # 4
        ]
        assert get_indentation(lines) == 4

    def test_non_positive_tab_size_raises_before_iterating(self):
        def gen():
            raise AssertionError("must not be iterated")
            yield "never"

        with pytest.raises(ValueError, match="tab_size must be positive"):
            get_indentation(gen(), tab_size=0)
