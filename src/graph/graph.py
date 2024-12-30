from collections import defaultdict
import osmnx as ox
import networkx as nx
import pandas as pd
import folium

class DisasterGraph:
    def __init__(self):
        self.graph = nx.Graph()
        self.emergency_services = {}  # Stores emergency service nodes
        self.shelters = {}           # Stores shelter nodes
        self.danger_zones = set()    # Stores current danger zones
        self.weights = defaultdict(lambda: 1)  # Default edge weight is 1

    def add_node(self, node_id, lat, lon):
        self.graph.add_node(node_id, y=lat, x=lon)

    def add_edge(self, node1, node2, weight):
        self.graph.add_edge(node1, node2, weight=weight)

    def add_danger_zone(self, lat, lon, radius):
        center_node = ox.nearest_nodes(self.graph, lon, lat)
        affected_nodes = nx.single_source_dijkstra_path_length(
            self.graph, 
            center_node, 
            cutoff=radius,
            weight='length'
        )
        self.danger_zones.update(affected_nodes.keys())
        for node in affected_nodes:
            for neighbor in self.graph.neighbors(node):
                self.weights[(node, neighbor)] = float('inf')

    def find_path(self, start_node, end_node):
        weighted_graph = self.graph.copy()
        edge_weights = {(u, v): self.weights[(u, v)] for u, v in weighted_graph.edges()}
        nx.set_edge_attributes(weighted_graph, edge_weights, 'weight')
        try:
            path = nx.shortest_path(weighted_graph, start_node, end_node, weight='weight')
            return path
        except nx.NetworkXNoPath:
            return None

    def update_map(self, save_path="test_path.html"):
        m = folium.Map(location=[33.6844, 73.0479], zoom_start=13)
        for node in self.graph.nodes:
            folium.CircleMarker(
                location=(self.graph.nodes[node]['y'], self.graph.nodes[node]['x']),
                radius=5,
                color='blue',
                fill=True,
                fill_color='blue'
            ).add_to(m)
        for u, v in self.graph.edges:
            folium.PolyLine(
                [(self.graph.nodes[u]['y'], self.graph.nodes[u]['x']),
                 (self.graph.nodes[v]['y'], self.graph.nodes[v]['x'])],
                color='blue'
            ).add_to(m)
        for zone in self.danger_zones:
            folium.Circle(
                location=(self.graph.nodes[zone]['y'], self.graph.nodes[zone]['x']),
                radius=1000,
                color='red',
                fill=True,
                fill_color='red'
            ).add_to(m)
        m.save(save_path)