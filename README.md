# jinja2-indent

A Jinja2 extension for managing indentation in templates.

[![PyPI](https://img.shields.io/pypi/v/jinja2-indent)](https://pypi.org/project/jinja2-indent/)
[![Python](https://img.shields.io/pypi/pyversions/jinja2-indent)](https://pypi.org/project/jinja2-indent/)
[![Build Status](https://github.com/dldevinc/jinja2-indent/actions/workflows/tests.yml/badge.svg)](https://github.com/dldevinc/jinja2-indent)
[![License](https://img.shields.io/pypi/l/jinja2-indent)](https://github.com/dldevinc/jinja2-indent/blob/master/LICENSE)

## Compatibility

- `python` >= 3.10
- `jinja2` >= 3.1

## Installation

Install the latest release with pip:

```shell
pip install jinja2-indent
```

## Usage

Add the extension to your Jinja2 environment:

```python
from jinja2 import Environment
from jinja2_indent import IndentExtension

env = Environment(extensions=[IndentExtension])
```

### `{% indent %}` tag

The tag adjusts the base indentation of the block content to the target
column. Relative offsets between lines are preserved: a line that was
indented N columns more than the current base indent stays N columns
more than the new base indent.

The argument can be:

- an integer — an absolute target column (`{% indent 4 %}`);
- a quoted string `"+N"` / `"-N"` — a shift relative to the current
base indent (`{% indent "+2" %}`).

An unquoted `-2` is an absolute (and therefore invalid) target: use
`"-2"` for a relative shift.

Only leading whitespace is affected. Blank and whitespace-only lines
are stripped of leading spaces and tabs, so increasing the indentation
never adds trailing whitespace to empty lines.

#### Increasing indentation

```jinja
root:
{% indent 2 -%}
- name: a
  value: 1
- name: b
  value: 2
- name: c
  value: 3
{%- endindent %}
```

```yaml
root:
  - name: a
    value: 1
  - name: b
    value: 2
  - name: c
    value: 3
```

#### Removing indentation (relative shift)

```jinja2
- name: a
  value: 1

{% if need_b %}{% indent "-2" -%}
  - name: b
    value: 2
{%- endindent %}{% endif %}

- name: c
  value: 3
```

```yaml
- name: a
  value: 1

- name: b
  value: 2

- name: c
  value: 3
```

#### Real-world example

```jinja2
services:
  {%- for name, service in services.items() %}{% indent "-2" %}
    {{ name }}:
      image: {{ service.image }}
      {%- if service.ports %}{% indent "-2" %}
        ports:
          {%- for port in service.ports %}
          - {{ port }}
          {%- endfor %}
      {%- endindent %}{% endif %}
  {%- endindent %}{% endfor %}

networks:
  default:
    name: {{ network_name }}
```

With

```python
context = {
    "services": {
        "web": {"image": "nginx:1.27", "ports": [80, 443]},
        "worker": {"image": "worker:latest", "ports": []},
    },
    "network_name": "app-net",
}
```

the template renders to:

```yaml
services:
  web:
    image: nginx:1.27
    ports:
      - 80
      - 443
  worker:
    image: worker:latest

networks:
  default:
    name: app-net
```

### `nindent` filter

A Helm-style filter: prepends a newline and indents every non-blank
line by the given number of spaces. The first line is always indented;
blank lines are not.

This is handy together with Jinja2's whitespace control:

```jinja
key:
  {{- "- a\n- b" | nindent(2) }}
```

```
key:
  - a
  - b
```

## Tab size

The `{% indent %}` tag accepts an optional `tab_size` argument, which
controls how a leading tab is expanded to columns when computing the
current indentation. It defaults to `4` and is only relevant for
templates that use tabs for indentation; space-only templates do not
need it.

```jinja
{% indent "-4", tab_size=8 -%}
	- name: a
{%- endindent %}
```

When the tag is used many times in a template, repeating `tab_size` is
inconvenient. Set the `indent__tab_size` template variable once instead:

```jinja
{% set indent__tab_size = 8 %}
{% indent "-4" -%}
	- name: a
{%- endindent %}
```
