# jinja2-indent

This Jinja2 extension adjusts the indentation of block content to a specified width.

[![PyPI](https://img.shields.io/pypi/v/jinja2-indent.svg)](https://pypi.org/project/jinja2-indent/)
[![Build Status](https://github.com/dldevinc/jinja2-indent/actions/workflows/tests.yml/badge.svg)](https://github.com/dldevinc/jinja2-indent)
[![Software license](https://img.shields.io/pypi/l/jinja2-indent.svg)](https://pypi.org/project/jinja2-indent/)

## Compatibility

-   `python` >= 3.9

## Installation

Install the latest release with pip:

```shell
pip install jinja2-indent
```

## Usage

The `{% indent %}` tag provided by this extension allows you to adjust the indentation level of the content inside the tag block. You can specify the desired width (in spaces), and the extension will reformat the content accordingly. This is particularly useful for aligning nested or indented structures in templates.

### Example

The following example demonstrates how to increase the indentation of a block of text:

```jinja2
root:
{% indent 2 %}
- name: a
  value: 1

- name: b
  value: 2

- name: c
  value: 3
{% endindent %}
```

```
root:
  - name: a
    value: 1

  - name: b
    value: 2

  - name: c
    value: 3
```

The following example demonstrates how to remove unnecessary indentation from a block of text:

```jinja2
- name: a
  value: 1

{% indent 0 %}
  - name: b
    value: 2
{% endindent %}

- name: c
  value: 3
```

```
- name: a
  value: 1

- name: b
  value: 2

- name: c
  value: 3
```
