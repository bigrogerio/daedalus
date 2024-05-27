import json
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network

with open("/Users/BRNGA049/Documents/carrefour/dag_parser/airflow2_dolphin_prd/airflow2_graph.json", "r") as f:
    adjacency_dict = json.load(f)

G_dir = nx.DiGraph()
G = nx.Graph()
G_dir.add_nodes_from(adjacency_dict.keys())

# Add edges from adjacency dictionary
print("Adding edges to graph")
for node, neighbors in adjacency_dict.items():
    for neighbor in neighbors:
        G_dir.add_edge(node, neighbor)
        G.add_edge(node, neighbor)

comps = sorted(nx.connected_components(G), key=len, reverse=True)
G_giant_dir = G_dir.subgraph(comps[0]).copy()

net = Network(
    directed=True,
    select_menu=True,  # Show part 1 in the plot (optional)
    filter_menu=True,  # Show part 2 in the plot (optional)
)
net.show_buttons()  # Show part 3 in the plot (optional)
net.from_nx(G_dir)  # Create directly from nx graph
net.show("airflow2.html", notebook=False)
