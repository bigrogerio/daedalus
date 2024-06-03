import ast
import argparse
import os
import fnmatch

def extract_imports(file_path):
    """
    Extracts all import statements from a given Python file.

    Parameters:
    file_path (str): The path to the Python file from which to extract import statements.

    Returns:
    list: A list of unique import statements found in the file.
    """
    with open(file_path, 'r') as file:
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

def find_python_files(directory='.'):
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
            if fnmatch.fnmatch(filename, '*.py'):
                # Construct full path to the Python file
                file_path = os.path.join(root, filename)
                python_files.append(file_path)

    return python_files

def extract_file_references(filename):
    """
    Extracts all file references from 'open' function calls in a given Python file.

    Parameters:
    filename (str): The path to the Python file from which to extract file references.

    Returns:
    list: A list of AST nodes representing the file references found in 'open' function calls.
    """
    open_file_references= []
    with open(filename, 'r') as file:
        tree = ast.parse(file.read(), filename=filename)
    for node in ast.walk(tree):
       if  isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id=='open':
                open_file_references.append(node.args[0])
    return open_file_references

def resolve_ast_name_assigns(ast_tree, variable_definitions={}):
    """
    Resolves assignments in an AST tree, updating variable states.

    Parameters:
    ast_tree (list): The abstract syntax tree (AST) containing nodes to resolve.
    variable_definitions (dict, optional): Dictionary of variable definitions to use in resolving Airflow variables.

    Returns:
    dict: A dictionary with variable names as keys and their resolved values.
    """
    assign_node_list=[node for node in ast_tree if isinstance(node, ast.Assign)]
    resolve_dict={}
    state={}
    for node in assign_node_list:
        for target in node.targets:
            resolve_dict[target]= node.value
    for key in resolve_dict.keys():
        if isinstance(key, ast.Name) and key.id in list(state.keys()):
            if isinstance(resolve_dict[key], ast.Constant):
                state[key.id]=ast.literal_eval(resolve_dict[key])
            elif isinstance(resolve_dict[key], ast.Name):
                state[key.id]=state[resolve_dict[key].id]
            elif is_airflow_variable_call(resolve_dict[key]):
                state[key.id]=resolve_airflow_variable(resolve_dict[key], variable_definitions)
            elif isinstance(resolve_dict[key], ast.JoinedStr):
                state[key.id]=resolve_joined_string(resolve_dict[key], state)
    return state

def resolve_joined_string(ast_JoinedStr_node, state):
    """
    Resolves a joined string node from an AST, replacing variables with their values.

    Parameters:
    ast_JoinedStr_node (ast.JoinedStr): The AST node representing the joined string.
    state (dict): Dictionary containing the current state of variable values.

    Returns:
    str: The resolved string with variables replaced by their values.
    """
    resolved=''
    if not isinstance(ast_JoinedStr_node, ast.JoinedStr):
        return resolved
    else:
        for value in ast_JoinedStr_node.values:
            if isinstance(value, ast.FormattedValue) and isinstance(value.value, ast.Name):
                if value.value.id in list(state):
                    resolved+=state[value.value.id]
            if isinstance(value, ast.Constant):
                resolved+=ast.literal_eval(value)
        return resolved
    
def is_airflow_variable_call(ast_node):
    """
    Checks if a given AST node represents an Airflow Variable.get() call.

    Parameters:
    ast_node (ast.AST): The AST node to check.

    Returns:
    bool: True if the node represents an Airflow Variable.get() call, False otherwise.
    """
    if isinstance(ast_node, ast.Call):
        if ast.dump(ast_node.func)=="Attribute(value=Name(id='Variable', ctx=Load()), attr='get', ctx=Load())":
            return True
    return False

def get_airflow_variable_from_call(ast_node):
    """
    Extracts the variable name from an Airflow Variable.get() call AST node.

    Parameters:
    ast_node (ast.AST): The AST node representing the Airflow Variable.get() call.

    Returns:
    str or None: The name of the variable if found, otherwise None.
    """
    if isinstance(ast_node, ast.Call):
        return ast_node.args[0].value
    return None

def resolve_airflow_variable(ast_node, variable_definitions):
    """
    Resolves the value of an Airflow variable from an AST node using provided variable definitions.

    Parameters:
    ast_node (ast.AST): The AST node representing the Airflow Variable.get() call.
    variable_definitions (dict): Dictionary containing variable definitions.

    Returns:
    str: The resolved variable value if found, otherwise 'undefined_variable_reference'.
    """
    if isinstance(ast_node, ast.Constant):
        if ast_node.args[0].value in list(variable_definitions.keys()):
            return variable_definitions[ast_node.args[0].value]
    return f'undefined_variable_reference'


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Resolve and analyze import statements in a Python file.')
    parser.add_argument('file_path', type=str, help='Path to the Python file')
    parser.add_argument('--analyze-imports', action='store_true', help='Flag to analyze import statements')
    parser.add_argument('--map-imports', action='store_true', help='Flag to map import tree to local file directories')
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
