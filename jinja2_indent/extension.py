import re

from collections.abc import Iterable, Iterator

from jinja2.filters import do_indent
from jinja2_simple_tags import ContainerTag


_INDENT_ARG_RE = re.compile(r"^([+-]?)(\d+)$")


class IndentExtension(ContainerTag):
    tags = {"indent"}

    # Template variable name to read tab size from.
    tab_size_var: str = "indent__tab_size"

    # Fallback tab size when the variable is not set.
    default_tab_size: int = 4

    def __init__(self, environment):
        super().__init__(environment)
        environment.filters["nindent"] = nindent

    def render(self, value: str | int, tab_size: int | None = None, caller=None):
        if tab_size is None:
            tab_size = self.context.get(self.tab_size_var, self.default_tab_size)
        tab_size = resolve_tab_size(tab_size)

        content = str(caller())
        lines = content.splitlines(keepends=True)

        current_indent = get_indentation(lines, tab_size=tab_size)
        target_indent = resolve_target_indent(value, current_indent)

        processed_lines = expand_leading_tabs(lines, tab_size=tab_size)
        processed_lines = reindent(processed_lines, current_indent, target_indent)
        return "".join(processed_lines)


def nindent(value: str, width: int = 4) -> str:
    """Add a leading newline and indent non-blank lines, like Helm's ``nindent``.

    Args:
        value: The value to indent.
        width: Number of leading spaces to add to each non-blank line,
            passed to Jinja2's ``indent`` filter.

    Returns:
        ``"\\n"`` followed by ``value`` indented by Jinja2's ``indent``
        filter with ``first=True`` and ``blank=False``.
    """
    return "\n" + do_indent(value, width=width, first=True, blank=False)


def resolve_tab_size(value: object) -> int:
    """Validate and normalize the tab size.

    Accepts integers and numeric strings like ``"4"``.
    The result must be a positive integer.

    Args:
        value: The raw tab size, typically from the template context.

    Returns:
        A positive integer tab size.

    Raises:
        ValueError: If ``value`` is a bool, not an int/numeric string, or
            not positive.
    """
    if isinstance(value, bool):
        raise ValueError(f"tab_size must be a positive integer, got {value!r}")
    if isinstance(value, int):
        tab_size = value
    elif isinstance(value, str):
        try:
            tab_size = int(value.strip())
        except ValueError:
            raise ValueError(f"tab_size must be a positive integer, got {value!r}") from None
    else:
        raise ValueError(f"tab_size must be a positive integer, got {value!r}")
    if tab_size <= 0:
        raise ValueError(f"tab_size must be positive, got {tab_size}")
    return tab_size


def resolve_target_indent(value: object, current_indent: int) -> int:
    """Resolve the ``{% indent ... %}`` argument to a target column.

    An integer (``{% indent 4 %}``) is an absolute target. A string of
    the form ``"+N"`` or ``"-N"`` (``{% indent "+2" %}``) is a relative
    shift from ``current_indent``. Relative shifts must be quoted; an
    unquoted ``-2`` is an absolute (and therefore invalid) target.

    Args:
        value: The tag argument as parsed by ``ContainerTag``.
        current_indent: Current base indentation in columns (>= 0).

    Returns:
        The target indentation in columns. May be negative if a relative
        shift moves below zero; the caller is responsible for rejecting
        that.

    Raises:
        ValueError: If ``value`` is neither an integer nor a string
            matching ``[+-]?\\d+``.
    """
    if isinstance(value, bool):
        raise ValueError(f"indent tag does not accept booleans: {value!r}")
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        raise ValueError(f"indent tag expects an integer or a string like '+N'/'-N', got {value!r}")
    match = _INDENT_ARG_RE.match(value.strip())
    if match is None:
        raise ValueError(f"indent tag expects an integer or a string like '+N'/'-N', got {value!r}")
    sign, digits = match.groups()
    n = int(digits)
    if sign == "+":
        return current_indent + n
    if sign == "-":
        return current_indent - n
    return n


def expand_leading_tabs(lines: Iterable[str], tab_size: int = 4) -> Iterator[str]:
    """Yield lines with tabs in the leading whitespace expanded to spaces.

    Only leading whitespace (spaces and tabs) before the first
    non-whitespace character is affected. A tab advances the column
    to the next multiple of `tab_size`. Line endings are preserved.

    Args:
        lines: Source lines, with or without line endings.
        tab_size: Tab width in columns; must be positive.

    Yields:
        Lines with expanded leading tabs.
    """
    if tab_size <= 0:
        raise ValueError(f"tab_size must be positive, got {tab_size}")

    for line in lines:
        # Find end of the leading whitespace prefix.
        i = 0
        n = len(line)
        while i < n and line[i] in " \t":
            i += 1
        prefix, rest = line[:i], line[i:]
        # str.expandtabs treats the prefix in isolation, which is exactly
        # the semantics we want: tabs are expanded starting from column 0.
        yield prefix.expandtabs(tab_size) + rest


def get_indentation(lines: Iterable[str], tab_size: int = 4) -> int:
    """Minimum leading indentation in columns among non-blank lines.

    A leading space is one column; a leading tab advances to the next
    multiple of `tab_size`. Only whitespace before the first
    non-whitespace character counts. Blank and whitespace-only lines
    are ignored. Returns 0 if there are no non-blank lines.
    """
    if tab_size <= 0:
        raise ValueError(f"tab_size must be positive, got {tab_size}")

    return min(
        (indent_of(line, tab_size) for line in lines if line.strip()),
        default=0,
    )


def indent_of(line: str, tab_size: int) -> int:
    """Leading indentation of `line` in columns.

    A leading space is one column; a leading tab advances the column
    to the next multiple of `tab_size`. Only whitespace before the first
    non-whitespace character counts. A blank or whitespace-only line
    yields the indentation of its entire length.

    Args:
        line: Source line (with or without line ending).
        tab_size: Tab width in columns; must be positive.

    Returns:
        Number of leading columns occupied by spaces and tabs.
    """
    col = 0
    for ch in line:
        if ch == " ":
            col += 1
        elif ch == "\t":
            col += tab_size - col % tab_size
        else:
            break
    return col


def reindent(
    lines: Iterable[str],
    current_indent: int,
    target_indent: int,
) -> Iterator[str]:
    """Re-align the leading indentation of every line.

    The relative offsets between lines are preserved: a non-blank line
    that was indented ``x`` columns more than ``current_indent`` becomes
    indented ``target_indent + (x - current_indent)`` columns. Blank and
    whitespace-only lines are stripped of their leading spaces and tabs,
    so increasing the indentation does not add trailing spaces to empty
    lines.

    Input lines are expected to have already been processed by
    :func:`expand_leading_tabs`: no line may start with a tab. Output
    indentation consists of spaces only.

    Args:
        lines: Source lines, with or without line endings.
        current_indent: Current base indentation in columns (>= 0).
            Must not exceed the indentation of any non-blank input line.
        target_indent: Desired base indentation in columns (>= 0).

    Yields:
        Re-indented lines with the same line endings as the input.

    Raises:
        ValueError: If ``current_indent`` or ``target_indent`` is
            negative, if a leading tab is found (``expand_leading_tabs``
            was not applied), or if a non-blank line is indented less
            than ``current_indent``.
    """
    if current_indent < 0:
        raise ValueError(f"current_indent must be >= 0, got {current_indent}")
    if target_indent < 0:
        raise ValueError(f"target_indent must be >= 0, got {target_indent}")

    delta = target_indent - current_indent

    for line in lines:
        if not line.strip(" \t\r\n"):
            if "\n" in line:
                yield line.lstrip(" \t")
            else:
                yield line
            continue

        body = line.rstrip("\r\n")
        ending = line[len(body) :]

        stripped = body.lstrip(" ")
        if stripped.startswith("\t"):
            raise ValueError(f"line starts with a tab; run expand_leading_tabs first: {line!r}")
        indent = len(body) - len(stripped)

        if indent < current_indent:
            raise ValueError(
                f"line indented {indent} columns, less than current_indent="
                f"{current_indent}: {line!r}"
            )

        yield " " * (indent + delta) + stripped + ending
