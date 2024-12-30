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
        
    def build_from_osm(self, city, country):
        """Build graph from OpenStreetMap data"""
        # Get road network
        self.graph = ox.graph_from_place(f"{city}, {country}", network_type='drive')
        self.graph = ox.distance.add_edge_lengths(self.graph)  # Add edge lengths in meters
        
    def load_emergency_services(self, filename=r'F:\AI\Project\Disaster-Response-System\src\graph\emergency_services.csv'):
        """Load emergency services into graph"""
        services_df = pd.read_csv(filename)
        
        for _, row in services_df.iterrows():
            # Find nearest node in road network
            nearest_node = ox.nearest_nodes(
                self.graph, 
                row['longitude'], 
                row['latitude']
            )
            
            # Store with type information
            self.emergency_services[nearest_node] = {
                'name': row['name'],
                'type': row['type'],
                'location': (row['latitude'], row['longitude'])
            }
            
    def load_shelters(self, filename=r'F:\AI\Project\Disaster-Response-System\src\graph\shelters.csv'):
        """Load shelter locations into graph"""
        shelters_df = pd.read_csv(filename)
        
        for _, row in shelters_df.iterrows():
            nearest_node = ox.nearest_nodes(
                self.graph, 
                row['longitude'], 
                row['latitude']
            )
            
            self.shelters[nearest_node] = {
                'name': row['name'],
                'capacity': row['capacity'],
                'location': (row['latitude'], row['longitude'])
            }
    
    def add_danger_zone(self, lat, lon, radius):
        """Add a danger zone affecting nearby nodes"""
        # Find center node
        center_node = ox.nearest_nodes(self.graph, lon, lat)
        
        # Find all nodes within radius
        affected_nodes = nx.single_source_dijkstra_path_length(
            self.graph, 
            center_node, 
            cutoff=radius,
            weight='length'
        )
        
        # Add affected nodes to danger zones
        self.danger_zones.update(affected_nodes.keys())
        
        # Update edge weights for affected areas
        for node in affected_nodes:
            for neighbor in self.graph.neighbors(node):
                self.weights[(node, neighbor)] = float('inf')
    
    def find_safe_path(self, start_lat, start_lon, end_lat, end_lon):
        """Find safest path between two points"""
        # Get nearest nodes to start and end points
        start_node = ox.nearest_nodes(self.graph, start_lon, start_lat)
        end_node = ox.nearest_nodes(self.graph, end_lon, end_lat)

        # Create a copy of graph with updated weights
        weighted_graph = self.graph.copy()
        edge_weights = {edge: self.weights[(edge[0], edge[1])] for edge in weighted_graph.edges}
        nx.set_edge_attributes(weighted_graph, edge_weights, 'weight')

        try:
            path = nx.shortest_path(weighted_graph, start_node, end_node, weight='weight')
            return path
        except nx.NetworkXNoPath:
            return None
    
    def get_number_of_danger_zones(self):
        """Return the number of danger zones"""
        return len(self.danger_zones)

    def visualize_graph(self, save_path="test_path.html"):
        """Visualize the graph with emergency services, shelters, and disaster zones"""
        # Create a map centered around Karachi
        m = folium.Map(location=[24.8607, 67.0011], zoom_start=13)
        
        # Add emergency services to the map
        for node, data in self.emergency_services.items():
            folium.Marker(
                location=data['location'],
                popup=f"{data['name']} ({data['type']})",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
        
        # Add shelters to the map
        for node, data in self.shelters.items():
            folium.Marker(
                location=data['location'],
                popup=f"{data['name']} (Capacity: {data['capacity']})",
                icon=folium.Icon(color='green', icon='home')
            ).add_to(m)
        
        # Add danger zones to the map as semi-transparent red circles
        for node in self.danger_zones:
            folium.Circle(
                location=(self.graph.nodes[node]['y'], self.graph.nodes[node]['x']),
                radius=1000,  # Adjust the radius as needed
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.5  # Semi-transparent
            ).add_to(m)
        
        # Save the map to an HTML file
        m.save(save_path)
        print(f"Graph visualization saved to {save_path}")