# Daedalus SDK

This is the **Daedalus** project, a software development kit for generating
graphs of repositories, focused on Airflow repos.

## Getting started

Daedalus main functionality to its users is the Command Line Interface (CLI)
executable, `daedalus-cli`, which the developers can use for creating templates for
all development steps in accordance with DevOps standards. Eventually it can
also be imported as regular python package for additional usage of its modules


# Contributing

Guidelines for Contributors:

- Simplicity First: The primary principle guiding Daedalus's development is
simplicity. It should focus on providing essential features for developers
without attempting to foresee all potential issues or abstract complex git
operations.

- Hands-off Approach: Our aim is not to babysit developers. Trust in their
expertise and let them navigate the git workflows as needed.

- Do not abuse from python looseness, always use type annotation, use ruff
LSP or linter attached to your code editor to automatically follow the
settings in `pyproject.toml`

- Tests for code standards are evaluated through [Ruff](https://docs.astral.sh/ruff/),
so we strongly advise using it as language server while writing code as it
is supported in many editors and is configured in `pyproject.toml` file

- Minimal use of Object-Oriented Programming(OOP) in Python Packages. Many
times, depending on the contributor's code style, it seems tempting to create
classes whenever possible. Avoid that as much as possible, our choices must
always pursue code simplicity and better maintainability

- In commit messages adopt the following keywords' convention:
    - (feat) Changes related to advances in implementing new features
    - (docs) Changes improving either functions or README documentation
    - (fix) Changes for fixes
    - (pkg) Changes in the package self configuration or continuous delivery
    - (refactor) Changes that should not affect user experience, to enhance code readability
    - Include a JIRA issue code if available

## Poetry packaging

[Poetry](https://python-poetry.org/) is an essential tool for python package
distribution, enabling complete configuration through the `pyproject.toml`
file. For contributors, understanding its basic functionality is crucial
despite all relevant settings should be ready to use, while editing `pyproject.toml`
is rare. If this tool is completely new take some time understanding it,
how it handles dependencies in groups, is extensible through plugins and
more importantly, some essential commands to work in local machine.

## Poetry self plugins

Some plugins are used to enhance Poetry functionality, aiming completeness within
a single tool. The following plugins attached to Poetry came from the following
requirements:

- Integrate `gitops` approach synchronizing the package version from commits
and tags with the version stated in `pyproject.toml` file dynamically

- Encapsulate and ease the call of commands or scripts in CI/CD `yaml` file
maintaining it reasonably clear

### Dynamic versioning

The poetry plugin `poetry-dynamic-versioning` is used for sync of versions
that must be provided in python files (`_version.py`) and `pyproject.toml`.
Check out https://pypi.org/project/poetry-dynamic-versioning/

Add as plugin:

```bash
poetry self add 'poetry-dynamic-versioning[plugin]'
```

**NOTE:** As the plugin is used for dynamic versioning, there is no need to
manually edit version fields in files

### Poe (The Poet) for general tasks definition

Running commands through poetry is better organized with the additional
plugin `poethepoet`. This plugin at first seems a little dispensable since all
tasks can be directly run in CI/CD steps, however, it provides a nice way to
run this tasks locally without a git event needed. Moreover, it cleans up the
CI/CD pipeline file abstracting some of the complexity, integrating nicely in
Poetry. Check out https://poethepoet.natn.io/index.html

Add Poe The Poet as plugin:

```bash
poetry self add 'poethepoet[poetry_plugin]'
```

**NOTE:** Be careful to not abuse from hooks and encapsulate too much of CI/CD
steps into poetry. The main reason for its adoption is just a thin layer of
abstraction and encapsulation into `pyproject.toml` file, besides leaving the
tasks available to run in a local environment.