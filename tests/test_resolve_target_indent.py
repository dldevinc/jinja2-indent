import pytest

from jinja2_indent.extension import resolve_target_indent


class TestResolveTargetIndent:
    def test_absolute_non_negative_int(self):
        assert resolve_target_indent(4, current_indent=0) == 4
        assert resolve_target_indent(0, current_indent=10) == 0

    def test_absolute_negative_int_returned_as_is(self):
        # negative int is an absolute target; caller (reindent) rejects it
        assert resolve_target_indent(-2, current_indent=10) == -2

    def test_relative_plus(self):
        assert resolve_target_indent("+2", current_indent=4) == 6
        assert resolve_target_indent("+0", current_indent=4) == 4

    def test_relative_minus(self):
        assert resolve_target_indent("-2", current_indent=4) == 2
        assert resolve_target_indent("-4", current_indent=4) == 0

    def test_relative_minus_below_zero_returns_negative(self):
        # resolve_target_indent does not clamp; reindent raises on negative
        assert resolve_target_indent("-10", current_indent=4) == -6

    def test_string_without_sign_is_absolute(self):
        assert resolve_target_indent("4", current_indent=100) == 4

    def test_whitespace_around_string(self):
        assert resolve_target_indent("  +2  ", current_indent=4) == 6

    @pytest.mark.parametrize("value", ["", "+", "-", "abc", "2.5", "+2.5", "++2", "+ 2"])
    def test_invalid_strings(self, value):
        with pytest.raises(ValueError, match="indent tag expects"):
            resolve_target_indent(value, current_indent=0)

    @pytest.mark.parametrize("value", [2.5, None, [], object()])
    def test_invalid_types(self, value):
        with pytest.raises(ValueError, match="indent tag expects"):
            resolve_target_indent(value, current_indent=0)

    def test_bool_rejected(self):
        with pytest.raises(ValueError, match="booleans"):
            resolve_target_indent(True, current_indent=0)
        with pytest.raises(ValueError, match="booleans"):
            resolve_target_indent(False, current_indent=0)
