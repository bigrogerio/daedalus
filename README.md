# Daedalus SDK
![telegram-cloud-photo-size-1-5057882066661780485-y](https://github.com/bigrogerio/daedalus/assets/62626374/2eec58ce-edf5-47ed-b2eb-e23105cc48d1)

This is the **Daedalus** project, a software development kit for generating
graphs of repositories, focused on Airflow repos.

## Getting started

Daedalus main functionality to its users is the Command Line Interface (CLI)
executable, `daedalus-cli`, which the developers can use for creating templates for
all development steps in accordance with DevOps standards. Eventually it can
also be imported as regular python package for additional usage of its modules

### Idea
Consider the usage of the `daedalus` package to facilitate the parsing of large airflow
directories in a visual way. The idea is to embed file dependency trees in a directed graph (DG)
and to use graph related algorithms to mathematically define complexity of the airflow environment,
critical points of failure, emerging design patterns, etc. By compiling the dependency trees as graphs
all DG analysis methods are trivially in scope, be it node-based, edge-based, motiff-based or subgraph-based
descriptors.
We work under the assumption that the `daedalus` package only has access to the directories of the airflow.
Which means we do not run `daedalus` in the run-time environment of the airflow DAGs, so that we assume that
all references to external variables and files are contained in `open` and `airflow.models.Variables` calls.
We then use the python Abstract Syntax Tree (AST) to resolve the first argument of `open` function calls, 
which gives us the referenced files, and the first argument of `airflow.models.Variables` calls which gives us
the path to pre-defined airflow variables.

We also assume that the airflow variables are present locally in a `variables.json` file, which is used to resolve
airflow variable referencing in the AST structure.

### Example
Consider the parsing of a typical `airflow` environment. 

- **dags/**: This folder contains all the DAG (Directed Acyclic Graph) definitions. Each Python file represents one or more DAGs. You can organize your DAGs into subfolders as needed.

- **plugins/**: This folder contains custom plugins. Each subfolder under plugins/ typically includes:
  - **operators/**: Custom operators.
  - **hooks/**: Custom hooks.
  - **sensors/**: Custom sensors.
  - **macros/**: Custom macros.
  - **helpers/**: Helper functions or classes.

- **tests/**: This folder contains test cases for your DAGs and plugins. Organized similarly to the plugins folder to keep tests for operators, hooks, sensors, macros, and helpers separate.

- **airflow.cfg**: The Airflow configuration file where you can set various parameters for your Airflow instance.

- **requirements.txt**: A file listing Python dependencies for your project. Useful for ensuring consistent environments across different setups.

We can use the `daedalus.dag_parse` module to generate a graph object in `networkx` and dinamically analyse it with the `pyvis` module.
Consider the following script:
```
import ast
import json
import re
from daedalus.daedalus.utils import dag_parse

airflow_patterns=[r'^functions', r'^operators']
dependency_graph={}

with open('path/to/variables.json','r') as f:
    variables=json.load(f)

python_files= dag_parse.find_python_files()

for file in python_files:
    with open(file, 'r') as f:
            tree = ast.parse(f.read(), filename=file)
            
    state=dag_parse.resolve_ast_name_assigns(ast.walk(tree), variables)
    open_file_references=[dag_parse.resolve_joined_string(node, state) for node in dag_parse.extract_file_references(file)]
    dependencies=[]

    for pattern in airflow_patterns:
            for import_stm in dag_parse.extract_imports(file):
                if re.match(pattern, import_stm):
                    import_stm=import_stm.replace('.','/')    
                    import_stm=re.sub(pattern, '/plugins/'+pattern[1:], import_stm)
                    dependencies.append(import_stm)

    dependency_graph[file]=(dependencies+open_file_references)

with open('airflow2_graph.json','w') as f:
    json.dump(dependency_graph,f)
```

- **Importing Modules**:
  - The script imports modules such as `ast`, `json`, and `re` for parsing Python code and handling JSON data.

- **Definitions**:
  - `airflow_patterns`: Contains regular expressions to match against import statements in Python files.
  - `dependency_graph`: Stores information about dependencies between Python files.

- **Processing Python Files**:
  - The script iterates over each Python file found in the Airflow project directory.
  - It parses each file into an abstract syntax tree (AST) and resolves variable assignments.
  - Dependencies are extracted from import statements and added to the dependency graph.

- **Writing Dependency Graph to JSON File**:
  - The final dependency graph is written to a JSON file named `airflow_dependency_graph.json`.


### Open Tasks

- [x] Separate airflow 1 and airflow 2 plugins and operators reference

# Contributing

Guidelines for Contributors:

- Simplicity First: The primary principle guiding Daedalus's development is
simplicity. It should focus on providing essential features for developers
without attempting to foresee all potential issues or abstract complex git
operations.

- Tests for code standards are evaluated through [Ruff](https://docs.astral.sh/ruff/),
so we strongly advise using it as language server while writing code as it
is supported in many editors and is configured in `pyproject.toml` file

- Minimal use of Object-Oriented Programming (OOP) in Python Packages. Many
times, depending on the contributor's code style, it seems tempting to create
classes whenever possible. Avoid that as much as possible, our choices must
always pursue code simplicity and better maintainability

- In commit messages adopt the following keywords' convention:
    - (feat) Changes related to advances in implementing new features
    - (docs) Changes improving either functions or README documentation
    - (fix) Changes for fixes
    - (pkg) Changes in the package self configuration or continuous delivery
    - (refactor) Changes that should not affect user experience, to enhance code readability

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
