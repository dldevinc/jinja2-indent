import itertools
import re
from typing import Generator

from jinja2_simple_tags import ContainerTag

re_initial_newline = re.compile(r"^\r?\n")
re_leading_spaces = re.compile(r"^([\s\t]*)(.*)")


class IndentExtension(ContainerTag):
    """
    A Jinja2 extension for managing indentation in templates.
    """

    tags = {"indent"}

    def render(self, width: int, keep_first_newline: bool = False, caller=None):
        """
        Render the content with adjusted indentation.

        Parameters:
        - width (int): Target indentation width.
        - keep_first_newline (bool, optional): Whether to keep the first newline.
        - caller (callable): A callable that provides the content to process.

        Returns:
        - str: The content with adjusted indentation.
        """
        content = caller()

        # Strip first newline
        if not keep_first_newline:
            content = re_initial_newline.sub("", content)

        # Split lines and expand tabs to spaces
        lines = split_and_expand_tabs(content)

        # Get current indentation level
        current_indentation = get_indentation(lines)

        # Calculate the shift needed for the desired indentation
        shift = max(-current_indentation, width - current_indentation)

        # Adjust lines and join them back together
        adjusted_lines = adjust_lines(lines, shift)
        return "\n".join(adjusted_lines)


def split_and_expand_tabs(text: str, tabsize: int = 4) -> list[str]:
    """
    Splits the given text into lines, preserving leading whitespace
    and replacing tabs with spaces.

    Parameters:
    - text (str): The input text to be split into lines.
    - tabsize (int, optional): The number of spaces to replace
        each tab character with. Default is 4.

    Returns:
    - list[str]: A list of lines with tabs replaced by the specified number
        of spaces, while maintaining the leading whitespace of each line.
    """
    lines = []
    for line in text.splitlines():
        match = re_leading_spaces.match(line)

        # Extract the leading whitespace characters (spaces and tabs)
        leading_spaces = match.group(1)

        # Extract the remaining content of the line
        content = match.group(2)

        # Replace all tabs with spaces, according to the specified tabsize
        lines.append(leading_spaces.expandtabs(tabsize) + content)

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


def adjust_lines(lines: list[str], shift: int) -> Generator[str, None, None]:
    """
    Adjust the indentation of each line by adding or removing spaces.

    Parameters:
    - lines (list[str]): A list of strings to adjust.
    - shift (int): The number of spaces to add (if positive) or remove (if negative).

    Yields:
    - str: The adjusted lines with modified indentation.
    """
    if not lines:
        return

    if not shift:
        yield from lines
        return

    for line in lines:
        if not line:
            yield line
        elif shift > 0:
            yield " " * shift + line
        else:
            yield line[-shift:]
