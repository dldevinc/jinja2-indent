from jinja2_indent.extension import adjust_lines, get_indentation, split_and_expand_tabs


class TestSplitAndExpandTabs:
    def test_empty_string(self):
        assert split_and_expand_tabs("") == []

    def test_only_whitespaces(self):
        assert split_and_expand_tabs("  ") == ["  "]

    def test_only_tabs(self):
        assert split_and_expand_tabs("\t\t") == [" " * 8]

    def test_whitespaces_with_tabs(self):
        assert split_and_expand_tabs("  \t  ") == [" " * 6]

    def test_multiline(self):
        # fmt: off
        assert split_and_expand_tabs(
            "  - name: a\n"
            "    value: 1\n"
            "  \n"
            "  - name: b\n"
            "    value: 2\n"
        ) == [
            "  - name: a",
            "    value: 1",
            "  ",
            "  - name: b",
            "    value: 2"
        ]
        # fmt: on


class TestGetIndentation:
    def test_empty_list(self):
        assert get_indentation([]) == 0

    def test_empty_line(self):
        assert get_indentation([""]) == 0

    def test_whitespace_lines_skipped(self):
        assert get_indentation([" " * 3, " " * 4, " " * 2]) == 0

    def test_multiline(self):
        # fmt: off
        assert get_indentation([
            "  - name: a",
            "    value: 1",
            "",
            "  - name: b",
            "    value: 2"
        ]) == 2
        # fmt: on


class TestAdjustLines:
    def test_empty_list(self):
        assert list(adjust_lines([], shift=4)) == []

    def test_empty_shift(self):
        assert list(adjust_lines(["  abc  "], shift=0)) == ["  abc  "]

    def test_positive_shift(self):
        # fmt: off
        assert list(adjust_lines([
            "  - name: a",
            "    value: 1",
            "",
            "  - name: b",
            "    value: 2"
        ], shift=2)) == [
            "    - name: a",
            "      value: 1",
            "",
            "    - name: b",
            "      value: 2"
        ]
        # fmt: on

    def test_negative_shift(self):
        # fmt: off
        assert list(adjust_lines([
            "  - name: a",
            "    value: 1",
            " ",
            "  - name: b",
            "    value: 2"
        ], shift=-2)) == [
            "- name: a",
            "  value: 1",
            "",
            "- name: b",
            "  value: 2"
        ]
        # fmt: on
