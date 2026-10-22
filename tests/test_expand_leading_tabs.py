import pytest

from jinja2_indent.extension import expand_leading_tabs


def _lines(text):
    """Split text the way the caller is now expected to."""
    return tuple(text.splitlines(keepends=True))


def _expand(text, tab_size=4):
    """Convenience: split, expand, and materialize the result as a list."""
    return list(expand_leading_tabs(_lines(text), tab_size=tab_size))


class TestExpandLeadingTabsBasics:
    def test_empty_text(self):
        assert list(expand_leading_tabs(())) == []

    def test_single_line_no_indent(self):
        assert _expand("hello") == ["hello"]

    def test_single_line_no_tabs(self):
        assert _expand("    hello") == ["    hello"]

    def test_single_tab(self):
        assert _expand("\thello") == ["    hello"]

    def test_two_tabs(self):
        assert _expand("\t\thello") == ["        hello"]

    def test_tab_after_spaces(self):
        # 1 space -> tab adds 3 -> 4
        assert _expand(" \thello") == ["    hello"]

    def test_spaces_after_tab(self):
        # tab (4) + 2 spaces -> 6
        assert _expand("\t  hello") == ["      hello"]

    def test_mixed_indentation(self):
        # "  \t hello": 2 -> tab adds 2 -> 4, then space -> 5
        assert _expand("  \t hello") == ["     hello"]

    def test_tab_size_three(self):
        assert _expand("  \thello", tab_size=3) == ["   hello"]
        assert _expand("\t\thello", tab_size=3) == ["      hello"]

    def test_tab_size_eight(self):
        assert _expand("\thello", tab_size=8) == ["        hello"]

    def test_tab_size_one(self):
        assert _expand("\thello", tab_size=1) == [" hello"]


class TestExpandLeadingTabsScope:
    def test_tabs_after_content_untouched(self):
        # Only the leading prefix is expanded.
        assert _expand("  hi\t\there") == ["  hi\t\there"]

    def test_tabs_in_content_untouched(self):
        assert _expand("code\ta\tb") == ["code\ta\tb"]

    def test_tab_after_non_ws_first_char(self):
        assert _expand("\thi\tthere") == ["    hi\tthere"]

    def test_only_leading_whitespace_expanded(self):
        assert _expand("\t  a\tb\n\t\tc\td") == ["      a\tb\n", "        c\td"]

    def test_trailing_tabs_in_blank_line(self):
        # Line is whitespace-only: whole line is the "leading prefix",
        # so all tabs are expanded.
        assert _expand("\t\t") == ["        "]

    def test_whitespace_only_line_mixed(self):
        assert _expand("   \t   ") == ["       "]


class TestExpandLeadingTabsLines:
    def test_multiple_lines(self):
        assert _expand("\tfoo\n  \tbar\nbaz") == [
            "    foo\n",
            "    bar\n",
            "baz",
        ]

    def test_preserves_trailing_newline(self):
        assert _expand("\tfoo\n") == ["    foo\n"]

    def test_no_trailing_newline(self):
        assert _expand("\tfoo") == ["    foo"]

    def test_blank_lines(self):
        assert _expand("\tfoo\n\n\tbar") == ["    foo\n", "\n", "    bar"]

    def test_crlf_preserved(self):
        assert _expand("\tfoo\r\n\tbar\r\n") == [
            "    foo\r\n",
            "    bar\r\n",
        ]

    def test_crlf_no_expand_inside_content(self):
        assert _expand("foo\tbar\r\n") == ["foo\tbar\r\n"]

    def test_empty_lines_only(self):
        assert _expand("\n\n\n") == ["\n", "\n", "\n"]

    def test_line_of_only_spaces(self):
        assert _expand("    \n") == ["    \n"]

    def test_custom_tab_size_multiple_lines(self):
        assert _expand("\ta\n\t\tb\n  \tc", tab_size=2) == [
            "  a\n",
            "    b\n",
            "    c",
        ]


class TestExpandLeadingTabsIsIterator:
    def test_returns_iterator(self):
        result = expand_leading_tabs(_lines("a\nb"))
        assert iter(result) is result

    def test_is_lazy(self):
        # Should not consume the input eagerly; check by taking only one item.
        it = expand_leading_tabs(_lines("\ta\n\tb\n\tc"))
        assert next(it) == "    a\n"

    def test_can_be_consumed_once(self):
        it = expand_leading_tabs(_lines("a\nb"))
        assert list(it) == ["a\n", "b"]
        assert list(it) == []


class TestExpandLeadingTabsValidation:
    def test_zero_tab_size_raises(self):
        with pytest.raises(ValueError):
            # The generator raises on the first iteration.
            _expand("a", tab_size=0)

    def test_negative_tab_size_raises(self):
        with pytest.raises(ValueError):
            _expand("a", tab_size=-4)

    def test_validation_happens_on_iteration(self):
        # Calling the generator function must not raise immediately.
        gen = expand_leading_tabs(_lines("a"), tab_size=0)
        with pytest.raises(ValueError):
            next(gen)


class TestExpandLeadingTabsEdgeCases:
    def test_unicode_content(self):
        assert _expand("\tпривет") == ["    привет"]

    def test_unicode_spaces_not_treated_as_whitespace(self):
        # NBSP is not in " \t", so it terminates the prefix.
        assert _expand("\t\u00a0x") == ["    \u00a0x"]

    def test_single_tab_only(self):
        assert _expand("\t") == ["    "]

    def test_large_tab_size(self):
        assert _expand("\tx", tab_size=100) == [" " * 100 + "x"]

    def test_many_tabs(self):
        assert _expand("\t" * 10) == [" " * 40]

    def test_consistency_with_str_expandtabs_on_prefix(self):
        # The expansion of the leading prefix must match str.expandtabs.
        for prefix in ["\t", " \t", "  \t", "\t\t", " \t \t", "\t  \t"]:
            line = prefix + "x"
            expected_prefix = prefix.expandtabs(4)
            assert _expand(line) == [expected_prefix + "x"]

    def test_newline_inside_prefix_terminates(self):
        # "\n" is not in " \t", so it ends the prefix and stays in place.
        assert _expand(" \nx") == [" \n", "x"]

    def test_carriage_return_terminates_prefix(self):
        assert _expand(" \rx") == [" \r", "x"]
