import nox


@nox.session(tags=["style", "fix"])
def black(session):
    session.install("black")
    session.run("black", "jinja2_indent", "tests")


@nox.session(tags=["style", "fix"])
def isort(session):
    session.install("isort")
    session.run("isort", "jinja2_indent", "tests")


@nox.session(tags=["style"])
def flake8(session):
    session.install("flake8", "flake8-pyproject")
    session.run("flake8", "jinja2_indent")


@nox.session(tags=["test"])
def pytest(session):
    session.install("poetry")
    session.run_install("poetry", "install", "--with", "pytest")
    session.run("poetry", "run", "pytest", "--cov", "--cov-report", "html", *session.posargs)
