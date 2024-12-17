import itertools
import re
from typing import Generator

from jinja2_simple_tags import ContainerTag

re_leading_spaces = re.compile(r"^([\s\t]*)(.*)")


class IndentExtension(ContainerTag):
    """
    A Jinja2 extension for managing indentation in templates.
    """

    tags = {"indent"}

    def render(self, target_indent: int, smart_ltrim: bool = True, first_line_indent: int = None, caller=None):
        """
        Render the content with adjusted indentation.

        Parameters:
        - target_indent (int): Target indentation width.
        - smart_ltrim (bool, optional): Whether to skip leading empty lines.
        - first_line_indent (int, optional): Number of spaces for the first line's indentation.
        - caller (callable): A callable that provides the content to process.

        Returns:
        - str: The content with adjusted indentation.
        """
        content = caller()

        if first_line_indent is None:
            first_line_indent = target_indent

        # Split lines and expand tabs to spaces
        lines = split_and_expand_tabs(content)

        # Determine the current indentation level
        current_indentation = get_indentation(lines)

        # Calculate the shift needed for the desired indentation
        shift = max(-current_indentation, target_indent - current_indentation)
        first_line_shift = max(-current_indentation, first_line_indent - current_indentation)

        # Apply indentation adjustments
        adjusted_lines = adjust_lines(lines, shift, first_line_shift=first_line_shift)

        # Optionally skip leading empty lines
        if smart_ltrim:
            adjusted_lines = itertools.dropwhile(lambda line: not line.strip(), adjusted_lines)

        return "\n".join(adjusted_lines)


def split_and_expand_tabs(text: str, tab_size: int = 4) -> list[str]:
    """
    Split the text into lines while replacing tabs with spaces.

    Parameters:
    - text (str): The input text to be split into lines.
    - tab_size (int, optional): Number of spaces for each tab. Default is 4.

    Returns:
    - list[str]: Lines with tabs replaced by spaces, preserving leading whitespace.
    """
    lines = []
    for line in text.splitlines():
        match = re_leading_spaces.match(line)

        # Extract leading whitespace and content
        leading_spaces = match.group(1)
        line_content = match.group(2)

        # Replace tabs with spaces in the leading whitespace
        lines.append(leading_spaces.expandtabs(tab_size) + line_content)

    return lines


def get_indentation(lines: list[str]) -> int:
    """
    Calculate the minimum indentation (number of leading spaces)
    of non-whitespace lines in a list of strings.

    Args:
        lines (list[str]): A list of strings to analyze for indentation.

    Returns:
        int: The minimum indentation of the non-whitespace lines.
             Returns 0 if all lines are empty or contain only whitespace.
    """
    if not lines:
        return 0

    indentation = float("inf")

    for line in lines:
        # Calculate the number of leading spaces in the current line
        line_indentation = sum(1 for _ in itertools.takewhile(str.isspace, line))

        # Skip whitespace-only lines
        if line_indentation == len(line):
            continue

        indentation = min(indentation, line_indentation)

    return indentation if indentation != float("inf") else 0


def adjust_lines(lines: list[str], shift: int, first_line_shift: int = None) -> Generator[str, None, None]:
    """
    Adjust the indentation of each line by adding or removing spaces.

    Parameters:
    - lines (list[str]): A list of strings to adjust.
    - shift (int): Spaces to add (positive) or remove (negative).
    - first_line_shift (int, optional): Shift value for the first line.

    Yields:
    - str: The adjusted lines with modified indentation.
    """
    if not lines:
        return

    first_line_processed = False
    if first_line_shift is None:
        first_line_shift = shift

    for line in lines:
        if not line:
            yield line
            continue

        if not first_line_processed:
            yield from _adjust_line(line, first_line_shift)
            first_line_processed = True
        else:
            yield from _adjust_line(line, shift)


def _adjust_line(line: str, shift: int) -> str:
    if shift == 0:
        yield line
    elif shift > 0:
        yield " " * shift + line
    else:
        yield line[-shift:]
