from jinja2 import Environment

from jinja2_indent import IndentExtension


class TestOneLine:
    def setup_method(self):
        self.env = Environment(extensions=[IndentExtension])

    def test_without_indentation(self):
        template = self.env.from_string("{% indent 4 %}data{% endindent %}")
        assert template.render({}) == "    data"

    def test_with_indentation_below_target(self):
        template = self.env.from_string("{% indent 4 %}  data{% endindent %}")
        assert template.render({}) == "    data"

    def test_with_indentation_above_target(self):
        template = self.env.from_string("{% indent 4 %}      data{% endindent %}")
        assert template.render({}) == "    data"

    def test_empty_line(self):
        template = self.env.from_string("{% indent 4 %}{% endindent %}")
        assert template.render({}) == ""


class TestMultiline:
    def setup_method(self):
        self.env = Environment(extensions=[IndentExtension])

    def test_without_indentation(self):
        # fmt: off
        template = self.env.from_string(
            "{% indent 4 %}\n"
            "data\n"
            "{% endindent %}"
        )
        assert template.render({}) == (
            "    data"
        )
        # fmt: on

    def test_with_indentation_below_target(self):
        # fmt: off
        template = self.env.from_string(
            "{% indent 4 %}\n"
            "  data\n"
            "{% endindent %}"
        )
        assert template.render({}) == (
            "    data"
        )
        # fmt: on

    def test_with_indentation_above_target(self):
        # fmt: off
        template = self.env.from_string(
            "{% indent 4 %}\n"
            "      data\n"
            "{% endindent %}"
        )
        assert template.render({}) == (
            "    data"
        )
        # fmt: on

    def test_empty_line(self):
        # fmt: off
        template = self.env.from_string(
            "{% indent 4 %}\n"
            "{% endindent %}"
        )
        assert template.render({}) == ""
        # fmt: on

    def test_no_smart_ltrim(self):
        # fmt: off
        template = self.env.from_string(
            "{% indent 4, smart_ltrim=False %}\n"
            "  - name: a\n"
            "    value: 1\n"
            "{% endindent %}"
        )
        assert template.render({}) == (
            "\n"
            "    - name: a\n"
            "      value: 1"
        )
        # fmt: on

    def test_first_line_indent(self):
        # fmt: off
        template = self.env.from_string(
            "  postrotate\n"
            "  {% indent 4, first_line_indent=2 %}\n"
            "  if [ -f /run/proc.pid ]; then\n"
            "    kill -HUP /run/proc.pid\n"
            "  fi\n"
            "  {%- endindent %}\n"
            "  endscript\n"
        )
        assert template.render() == (
            "  postrotate\n"
            "    if [ -f /run/proc.pid ]; then\n"
            "      kill -HUP /run/proc.pid\n"
            "    fi\n"
            "  endscript"
        )
        # fmt: on
