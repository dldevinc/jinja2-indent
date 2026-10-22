import nox


@nox.session(tags=["dev"])
def ruff(session: nox.Session) -> None:
    """Fix lint issues and format source code."""
    session.install("ruff")
    paths = session.posargs or ["jinja2_indent"]
    session.run("ruff", "check", "--fix", *paths)
    session.run("ruff", "format", *paths)


@nox.session(tags=["ci"])
def ruff_ci(session: nox.Session) -> None:
    """Check lint and formatting without modifying files."""
    session.install("ruff")
    paths = session.posargs or ["jinja2_indent"]
    session.run("ruff", "check", *paths)
    session.run("ruff", "format", "--check", *paths)


@nox.session(tags=["dev"])
def pytest(session: nox.Session) -> None:
    """Run tests with an HTML coverage report."""
    session.run(
        "poetry",
        "install",
        "--with",
        "pytest",
        external=True,
        env={"POETRY_VIRTUALENVS_CREATE": "false"},
    )

    session.run(
        "pytest",
        "--cov=jinja2_indent",
        "--cov-report=term-missing",
        "--cov-report=html",
        *session.posargs,
    )


@nox.session(tags=["ci"])
def pytest_ci(session: nox.Session) -> None:
    """Run tests with CI-friendly coverage output."""
    session.run(
        "poetry",
        "install",
        "--with",
        "pytest",
        external=True,
        env={"POETRY_VIRTUALENVS_CREATE": "false"},
    )

    session.run(
        "pytest",
        "--cov=jinja2_indent",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-report=xml:coverage.xml",
        *session.posargs,
    )
