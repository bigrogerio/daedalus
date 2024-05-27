from dag_parse import extract_imports, find_python_files, extract_file_references
import re
import json

# python_files=find_python_files()
# import_trees={}
# airflow_patterns=[r'^functions', r'^operators']

# for file in python_files:
#     dependencies=[]
#     for pattern in airflow_patterns:
#         for import_stm in extract_imports(file):
#             if re.match(pattern, import_stm):
#                 import_stm=import_stm.replace('.','/')
#                 import_stm=re.sub(pattern, '/plugins/'+pattern[1:], import_stm)
#                 dependencies.append(import_stm)
#     import_trees[file]=dependencies

# print(import_trees)
# with open('dag_dependencies_full.json','w') as f:
#     json.dump(import_trees,f)

file_references = extract_file_references(
    "/Users/BRNGA049/Documents/carrefour/dag_parser/airflow2_dolphin_prd/dags/cadgold/ingestion_carteira_pedidos.py"
)
print(file_references)

# for file in python_files:
#     dependencies=[]
#     for pattern in airflow_patterns:
#         for import_stm in extract_imports(file):
#             if re.match(pattern, import_stm):
#                 import_stm=import_stm.replace('.','/')
#                 import_stm=re.sub(pattern, '/plugins/'+pattern[1:], import_stm)
#                 dependencies.append(import_stm)
#     import_trees[file]=dependencies
