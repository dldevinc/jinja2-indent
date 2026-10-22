import pytest

from jinja2 import Environment

from jinja2_indent.extension import IndentExtension


@pytest.fixture
def env() -> Environment:
    return Environment(extensions=[IndentExtension])


def render(env: Environment, source: str, **context) -> str:
    return env.from_string(source).render(**context)


class TestNindentFilter:
    def test_basic(self, env):
        source = (
            'key:{{ "a\\nb" | nindent(2) }}'
        )
        expected = (
            "key:\n"
            "  a\n"
            "  b"
        )
        assert render(env, source) == expected

    def test_first_line_indented(self, env):
        source = (
            '{{ "a\\nb" | nindent(4) }}'
        )
        expected = (
            "\n"
            "    a\n"
            "    b"
        )
        assert render(env, source) == expected

    def test_default_width_is_four(self, env):
        source = (
            '{{ "a\\nb" | nindent }}'
        )
        expected = (
            "\n"
            "    a\n"
            "    b"
        )
        assert render(env, source) == expected

    def test_blank_lines_stay_empty(self, env):
        source = (
            '{{ "a\\n\\nb" | nindent(2) }}'
        )
        expected = (
            "\n"
            "  a\n"
            "\n"
            "  b"
        )
        assert render(env, source) == expected

    def test_trailing_newline_preserved(self, env):
        source = (
            '{{ "a\\nb\\n" | nindent(2) }}'
        )
        expected = (
            "\n"
            "  a\n"
            "  b\n"
        )
        assert render(env, source) == expected

    def test_empty_value(self, env):
        source = (
            '{{ "" | nindent(2) }}'
        )
        expected = "\n  "
        assert render(env, source) == expected

    def test_non_string_value(self, env):
        source = (
            "{{ 42 | nindent(2) }}"
        )
        with pytest.raises(TypeError):
            render(env, source)

    def test_zero_width(self, env):
        source = (
            '{{ "a\\nb" | nindent(0) }}'
        )
        expected = (
            "\n"
            "a\n"
            "b"
        )
        assert render(env, source) == expected

    def test_chomps_left_newline(self, env):
        source = (
            "key:\n"
            "{{- '- a\\n- b' | nindent(2) }}"
        )
        expected = (
            "key:\n"
            "  - a\n"
            "  - b"
        )
        assert render(env, source) == expected


class TestIndentTag:
    def test_absolute(self, env):
        source = (
            "root:\n"
            "{% indent 2 -%}\n"
            "- a: 1\n"
            "- b: 2\n"
            "{%- endindent %}"
        )
        expected = (
            "root:\n"
            "  - a: 1\n"
            "  - b: 2"
        )
        assert render(env, source) == expected

    def test_absolute_zero_removes_indent(self, env):
        source = (
            "{% indent 0 %}\n"
            "    a\n"
            "    b\n"
            "{%- endindent %}"
        )
        expected = (
            "\n"
            "a\n"
            "b"
        )
        assert render(env, source) == expected

    def test_relative_plus(self, env):
        source = (
            '{% indent "+2" %}\n'
            "  a\n"
            "  b\n"
            "{%- endindent %}"
        )
        expected = (
            "\n"
            "    a\n"
            "    b"
        )
        assert render(env, source) == expected

    def test_relative_minus(self, env):
        source = (
            '{% indent "-2" %}\n'
            "    a\n"
            "    b\n"
            "{%- endindent %}"
        )
        expected = (
            "\n"
            "  a\n"
            "  b"
        )
        assert render(env, source) == expected

    def test_blank_lines_stay_empty(self, env):
        source = (
            "{% indent 4 -%}\n"
            "a\n"
            "\n"
            " b\n"
            "{%- endindent %}"
        )
        expected = (
            "    a\n"
            "\n"
            "     b"
        )
        assert render(env, source) == expected

    def test_nested_indent_blocks(self, env):
        source = (
            "{% indent 2 -%}\n"
            "a\n"
            "{% indent 2 -%}\n"
            "b\n"
            "{%- endindent %}\n"
            "{%- endindent %}"
        )
        expected = (
            "  a\n"
            "    b"
        )
        assert render(env, source) == expected

    def test_nested_indent_blocks_formatted(self, env):
        source = (
            "{% indent 2 %}\n"
            "  a\n"
            "  {% indent 2 %}\n"
            "    b\n"
            "  {%- endindent %}\n"
            "{%- endindent %}"
        )
        expected = (
            "\n"
            "  a\n"
            "\n"
            "  b"
        )
        assert render(env, source) == expected


class TestIndentTagWhitespace:
    def test_without_minus_leading_newline_is_kept(self, env):
        # Without '-' the newline after {% indent %} is part of the
        # block content and becomes an empty line in the output.
        source = (
            "{% indent 2 %}\n"
            "- a: 1\n"
            "{%- endindent %}"
        )
        assert render(env, source) == "\n  - a: 1"

    def test_without_minus_trailing_newline_is_kept(self, env):
        # Without '-' the newline before {% endindent %} is part of
        # the block content and becomes a trailing empty line.
        source = (
            "{% indent 2 -%}\n"
            "- a: 1\n"
            "{% endindent %}"
        )
        assert render(env, source) == "  - a: 1\n"

    def test_without_minus_both_newlines_kept(self, env):
        source = (
            "{% indent 2 %}\n"
            "- a: 1\n"
            "{% endindent %}"
        )
        # Leading '\n' from the opening tag, trailing '\n' from the
        # closing tag (the final one is not stripped by Jinja2 because
        # the template does not end with a newline).
        assert render(env, source) == "\n  - a: 1\n"


class TestIndentTagInContext:
    def test_tag_with_indent_in_middle_of_template(self, env):
        source = (
            "before\n"
            "  {% indent 2 %}\n"
            "      a\n"
            "  {% endindent %}\n"
            "\n"
            "after"
        )
        expected = (
            "before\n"
            "  \n"
            "  a\n"
            "  \n"
            "\n"
            "after"
        )
        assert render(env, source) == expected

    def test_newline_after_endindent_separates_block_from_content(self, env):
        source = (
            "{% indent 2 -%}\n"
            "- a: 1\n"
            "{%- endindent %}\n"
            "after"
        )
        expected = (
            "  - a: 1\n"
            "after"
        )
        assert render(env, source) == expected

    def test_block_at_end_of_template(self, env):
        source = (
            "root:\n"
            "{% indent 2 -%}\n"
            "- a: 1\n"
            "{%- endindent %}"
        )
        expected = (
            "root:\n"
            "  - a: 1"
        )
        assert render(env, source) == expected


class TestIndentTagEdges:
    def test_two_leading_newlines_keep_both(self, env):
        source = (
            "{% indent 2 %}\n"
            "\n"
            "- a: 1\n"
            "{%- endindent %}"
        )
        expected = (
            "\n"
            "\n"
            "  - a: 1"
        )
        assert render(env, source) == expected

    def test_two_trailing_newlines_keep_both(self, env):
        source = (
            "{% indent 2 -%}\n"
            "- a: 1\n"
            "\n"
            "{% endindent %}"
        )
        assert render(env, source) == "  - a: 1\n\n"

    def test_crlf_template_is_normalized_to_lf(self, env):
        # Jinja2 normalizes CRLF to LF by default (newline_sequence="\n").
        source = (
            "root:\r\n"
            "{% indent 2 -%}\r\n"
            "- a: 1\r\n"
            "{%- endindent %}"
        )
        expected = (
            "root:\n"
            "  - a: 1"
        )
        assert render(env, source) == expected


class TestIndentTagTabSize:
    def test_tab_size_from_template_variable(self, env):
        source = (
            '{% indent "+1" %}\n'
            "\ta\n"
            "{%- endindent %}"
        )
        expected = (
            "\n"
            "   a"
        )
        assert render(env, source, indent__tab_size=2) == expected

    def test_tab_size_default(self, env):
        source = (
            '{% indent "+1" %}\n'
            "\ta\n"
            "{%- endindent %}"
        )
        expected = (
            "\n"
            "     a"
        )
        assert render(env, source) == expected

    def test_tab_size_string_from_context(self, env):
        source = (
            '{% indent "+1" %}\n'
            "\ta\n"
            "{%- endindent %}"
        )
        expected = (
            "\n"
            "   a"
        )
        assert render(env, source, indent__tab_size="2") == expected

    @pytest.mark.parametrize("bad", [0, -4, "0", "-4", "abc", "", True, False, 2.5, None])
    def test_invalid_tab_size_from_context_raises(self, env, bad):
        source = (
            '{% indent "+1" %}\n'
            "\ta\n"
            "{%- endindent %}"
        )
        with pytest.raises(ValueError, match="tab_size"):
            render(env, source, indent__tab_size=bad)


class TestIndentTagErrors:
    def test_relative_below_zero_raises(self, env):
        source = (
            '{% indent "-4" %}\n'
            "  a\n"
            "{%- endindent %}"
        )
        with pytest.raises(ValueError, match="target_indent"):
            render(env, source)

    def test_unquoted_minus_is_absolute_and_rejected(self, env):
        source = (
            "{% indent -2 %}\n"
            "  a\n"
            "{%- endindent %}"
        )
        with pytest.raises(ValueError, match="target_indent"):
            render(env, source)

    def test_unquoted_plus_collapses_to_absolute(self, env):
        source = (
            "{% indent +2 %}\n"
            "    a\n"
            "{%- endindent %}"
        )
        expected = (
            "\n"
            "  a"
        )
        assert render(env, source) == expected

    def test_invalid_argument(self, env):
        source = (
            '{% indent "abc" %}\n'
            "a\n"
            "{%- endindent %}"
        )
        with pytest.raises(ValueError, match="indent tag expects"):
            render(env, source)

    def test_non_integer_argument(self, env):
        source = (
            "{% indent 2.5 %}\n"
            "a\n"
            "{%- endindent %}"
        )
        with pytest.raises(ValueError, match="indent tag expects"):
            render(env, source)


class TestIndentTagRealWorld:
    def test_yaml_config_with_loop_and_condition(self, env):
        source = (
            "services:\n"
            "  {%- for name, service in services.items() %}{% indent '-2' %}\n"
            "    {{ name }}:\n"
            "      image: {{ service.image }}\n"
            "      {%- if service.ports %}{% indent '-2' %}\n"
            "        ports:\n"
            "          {%- for port in service.ports %}\n"
            "          - {{ port }}\n"
            "          {%- endfor %}\n"
            "      {%- endindent %}{% endif %}\n"
            "  {%- endindent %}{% endfor %}\n"
            "\n"
            "networks:\n"
            "  default:\n"
            "    name: {{ network_name }}\n"
        )
        context = {
            "services": {
                "web": {"image": "nginx:1.27", "ports": [80, 443]},
                "worker": {"image": "worker:latest", "ports": []},
            },
            "network_name": "app-net",
        }
        expected = (
            "services:\n"
            "  web:\n"
            "    image: nginx:1.27\n"
            "    ports:\n"
            "      - 80\n"
            "      - 443\n"
            "  worker:\n"
            "    image: worker:latest\n"
            "\n"
            "networks:\n"
            "  default:\n"
            "    name: app-net"
        )
        assert render(env, source, **context) == expected
