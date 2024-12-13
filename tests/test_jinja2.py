from jinja2 import Environment

from jinja2_indent import IndentExtension


class TestExtension:
    def setup_method(self):
        self.env = Environment(extensions=[IndentExtension])

    def test_one_line(self):
        template = self.env.from_string("{% indent 4 %}value: 1{% endindent %}")
        assert template.render({}) == "    value: 1"

    def test_multiline_template(self):
        # fmt: off
        template = self.env.from_string(
            "{% indent 0 %}\n"
            "  - name: a\n"
            "    value: 1\n"
            "{% endindent %}"
        )
        assert template.render({}) == (
            "- name: a\n"
            "  value: 1"
        )
        # fmt: on

    def test_yaml_template(self):
        template = self.env.from_string(
            "- name: a\n"
            "  value: 1\n"
            "{% if b %}{% indent 0 %}\n"
            "  - name: b\n"
            "    value: 2\n"
            "{% endindent %}{% endif %}\n"
            "- name: c\n"
            "  value: 3\n"
        )
        assert template.render({"b": True}) == (
            "- name: a\n"
            "  value: 1\n"
            "- name: b\n"
            "  value: 2\n"
            "- name: c\n"
            "  value: 3"
        )
