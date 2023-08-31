# Contributing to Django Ninja CRUD

We welcome contributions to Django-Ninja-CRUD! This document outlines how to contribute to this project and provides guidelines to make the process smoother for everyone involved.

For an overview of how to contribute to open-source projects on GitHub, see [GitHub's official documentation](https://docs.github.com/en/get-started/exploring-projects-on-github/finding-ways-to-contribute-to-open-source-on-github).

## Table of Contents
- [Setting up Development Environment](#setting-up-development-environment)
- [Running Tests](#running-tests)
- [Coding and Commit Conventions](#coding-and-commit-conventions)
- [Labels for Issues and PRs](#labels-for-issues-and-prs)
- [Updating an Existing Pull Request](#updating-an-existing-pull-request)

## Setting up Development Environment

1. **Install Python 3.x**: Make sure Python 3.x is installed on your machine.

2. **Create a Virtual Environment**:
    ```bash
    python3 -m venv venv
    ```

3. **Activate the Virtual Environment**:
    ```bash
    source venv/bin/activate
    ```

4. **Install Poetry**:
    ```bash
    pip install poetry
    ```

5. **Install Project Dependencies**:
    ```bash
    poetry install
    ```

6. **Install Pre-commit Hooks**: To ensure code quality, we use pre-commit hooks. Install the pre-commit package and set up the hooks with:
    ```bash
    pip install pre-commit
    pre-commit install
    ```
    This will automatically run checks before each commit, helping you adhere to the coding and commit conventions.

## Running Tests

After setting up your development environment, you can run tests to make sure everything is functioning as expected. To run the tests, use the following commands:

```bash
export DJANGO_SETTINGS_MODULE=tests.test_settings
python -m poetry run coverage run -m django test
python -m poetry run coverage report
```

## Coding and Commit Conventions

- We adhere to the [PEP 8](https://pep8.org/) coding style guide.
- For commits, we follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Labels for Issues and PRs

We use a set of labels to categorize issues and pull requests. This helps in project management and prioritizing work.

- **bug**: For marking issues that are bugs.
- **enhancement**: For new features or improvements.
- **documentation**: Issues related to documentation.
- **good first issue**: Easier issues aimed at beginners.
- **help wanted**: Issues that need additional support.

## Updating an Existing Pull Request

1. **Ensure Your Fork is Up-to-date**:
    ```bash
    git remote add upstream https://github.com/hbakri/django-ninja-crud.git
    git fetch upstream
    ```

2. **Check Out Your Local Branch**: Associated with the PR.

3. **Rebase Your Branch**:
    ```bash
    git rebase upstream/main
    ```

4. **Resolve Conflicts**: If conflicts arise, resolve them.

5. **Commit Your Changes**.

6. **Force Push to Update the PR**:
    ```bash
    git push origin <your-branch> --force
    ```

---

Thank you for contributing to `django-ninja-crud`! Your efforts help make this project better for everyone.
