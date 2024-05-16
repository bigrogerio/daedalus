import ast
import argparse
import os
import fnmatch


def extract_imports(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read(), filename=file_path)

    imports = set()

    # Traverse the AST and collect import statements
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module
            for alias in node.names:
                import_name = f"{module_name}.{alias.name}"
                imports.add(import_name)

    return list(imports)


def find_python_files(directory="."):
    """
    Recursively find all Python (*.py) files within the specified directory and its subdirectories.

    Args:
        directory (str): The directory path to start searching (default is current working directory).

    Returns:
        list: A list of paths to all Python (*.py) files found.
    """
    python_files = []

    # Traverse directory recursively
    for root, dirs, files in os.walk(directory):
        for filename in files:
            # Check if file has .py extension
            if fnmatch.fnmatch(filename, "*.py"):
                # Construct full path to the Python file
                file_path = os.path.join(root, filename)
                python_files.append(file_path)

    return python_files


def extract_file_references(filename):
    file_references = []

    # Parse the Python file into an AST
    with open(filename, "r") as f:
        tree = ast.parse(f.read(), filename=filename)

    # Traverse the AST nodes
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "open"
        ):
            # Found an 'open()' function call
            print(node)
            print(node.args)
            for arg in node.args:
                print(eval(arg))
            if len(node.args) >= 1 and isinstance(node.args[0], ast.Str):
                # Extract the file path argument passed to 'open()'
                file_path = node.args[0].s
                file_references.append(file_path)

    return file_references


def resolve_ast_name_assigns(assign_node_list, variable_definitions={}):
    resolve_dict = {}
    state = {}
    for node in assign_node_list:
        for target in node.targets:
            resolve_dict[target] = node.value
    for key in resolve_dict.keys():
        if isinstance(resolve_dict[key], ast.Constant):
            state[key.id] = ast.literal_eval(resolve_dict[key])
        elif isinstance(resolve_dict[key], ast.Name):
            state[key.id] = state[resolve_dict[key].id]
        elif is_airflow_variable_call(resolve_dict[key]):
            state[key.id] = resolve_airflow_variable(
                resolve_dict[key], variable_definitions
            )
    return state


def is_airflow_variable_call(ast_node):
    if isinstance(ast_node, ast.Call):
        if (
            ast.dump(ast_node.func)
            == "Attribute(value=Name(id='Variable', ctx=Load()), attr='get', ctx=Load())"
        ):
            return True
    return False


def get_airflow_variable_from_call(ast_node):
    if isinstance(ast_node, ast.Call):
        return ast_node.args[0].value
    return None


def resolve_airflow_variable(ast_node, variable_definitions):
    return variable_definitions[ast_node.args[0].value]


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Resolve and analyze import statements in a Python file."
    )
    parser.add_argument("file_path", type=str, help="Path to the Python file")
    parser.add_argument(
        "--analyze-imports",
        action="store_true",
        help="Flag to analyze import statements",
    )
    parser.add_argument(
        "--map-imports",
        action="store_true",
        help="Flag to map import tree to local file directories",
    )
    args = parser.parse_args()

    if args.analyze_imports:
        # Extract import trees
        extracted_imports = extract_imports(args.file_path)

        # Print extracted import trees
        print("Extracted Import Trees:")
        for path in extracted_imports:
            print(path)


if __name__ == "__main__":
    main()
