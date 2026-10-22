# Change Log

## [1.0.0b1](https://github.com/dldevinc/jinja2-indent/releases/tag/v1.0.0b1) - 2026-10-22

Complete rewrite of the extension.

- Requires Python >= 3.10.
- Added relative arguments: `"+N"` and `"-N"` shift the current base indentation.
- Added tab support: leading tabs are expanded before reindentation; tab size can be set via the `indent__tab_size` template variable (default 4).
- Added the `nindent` filter (Helm-style: prepends a newline and indents every non-blank line).
- Switched to `ruff` for linting and formatting; added coverage reports to the test sessions.

## [0.3.0](https://github.com/dldevinc/jinja2-indent/releases/tag/v0.3.0) - 2024-12-17

- Added `smart_ltrim` and `first_line_indent` arguments.
- Removed `keep_first_newline` argument.

## [0.2.0](https://github.com/dldevinc/jinja2-indent/releases/tag/v0.2.0) - 2024-12-17

- Added `keep_first_newline` argument.

## [0.1.0](https://github.com/dldevinc/jinja2-indent/releases/tag/v0.1.0) - 2024-12-13

- First release
