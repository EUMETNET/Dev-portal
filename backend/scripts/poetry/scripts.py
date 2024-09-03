"""
Scripts to be run with 'poetry run' command.
Poetry cannot run shell scripts in its scripts section, so we have to use Python scripts instead.
"""

import subprocess
import os


def format_code() -> None:
    """
    Format the code using black
    """
    subprocess.run(["black", "app/"], check=False)


def format_code_check() -> None:
    """
    Check if the code is formatted correctly using black
    """
    subprocess.run(["black", "--check", "app/"], check=True)


def lint_code() -> None:
    """
    Lint the code using pylint
    """
    subprocess.run(["pylint", "app/"], check=True)


def type_check() -> None:
    """
    Type check the code using mypy
    """
    subprocess.run(["mypy", "app/"], check=True)


def security_check() -> None:
    """
    Check for security vulnerabilities using bandit
    """
    subprocess.run(["bandit", "-r", "app"], check=True)


def run_tests() -> None:
    """
    Run the tests using pytest
    """

    # Check if SECRETS_FILE is set, otherwise default to secrets.test.yaml
    secrets_file = os.getenv("SECRETS_FILE", "secrets.test.yaml")
    os.environ["SECRETS_FILE"] = secrets_file

    # Pass the current environment variables to the subprocess
    env = os.environ.copy()
    subprocess.run(["pytest"], check=False, env=env)
