from graph_structure import DisasterGraph

# Initialize the graph
disaster_graph = DisasterGraph()

# Add nodes (example coordinates; replace with real data)
disaster_graph.add_node(1, 33.6844, 73.0479)
disaster_graph.add_node(2, 33.7000, 73.1000)
disaster_graph.add_node(3, 33.7100, 73.0500)

# Add edges (example weights; replace with real data)
disaster_graph.add_edge(1, 2, weight=5)
disaster_graph.add_edge(2, 3, weight=3)
disaster_graph.add_edge(1, 3, weight=8)

# Add a danger zone
disaster_graph.add_danger_zone(lat=33.6900, lon=73.0900, radius=1000)

# Find the shortest safe path
path = disaster_graph.find_path(1, 3)
print(f"Shortest safe path: {path}")

# Generate the map
disaster_graph.update_map(save_path="test_path.html")