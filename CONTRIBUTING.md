# Contribution

## Development

### Setup

1. Make sure you have [pipx](https://pipx.pypa.io/stable/installation/) installed.
1. Install [poetry](https://python-poetry.org/docs/#installation)
   ```shell
   pipx install poetry
   ```
1. Install [nox](https://nox.thea.codes/en/stable/tutorial.html#installation)
   ```shell
   pipx install nox
   ```

1. Clone the repository:
   ```shell
   git clone https://github.com/dldevinc/jinja2-indent
   ```
1. Navigate to the project root directory:
   ```shell
   cd jinja2-indent
   ```
1. Install python dependencies:
   ```shell
   poetry install
   ```

### Formatting

To run `black`, `isort` and `flake8`:

```shell
nox -Rt style fix
```

### Testing

To run unit tests:

```shell
nox -Rt test
```
