from collections import defaultdict
import osmnx as ox
import networkx as nx
import pandas as pd
import folium
import math

class DisasterGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.emergency_services = {}  # Stores emergency service nodes
        self.shelters = {}           # Stores shelter nodes
        self.danger_zones = set()    # Stores current danger zones
        self.weights = defaultdict(lambda: 1)  # Default edge weight is 1
        
    def build_from_osm(self, place_name):
        """Build graph from OpenStreetMap data"""
        # Get road network
        self.graph = ox.graph_from_place(place_name, network_type='drive')
        self.graph = ox.distance.add_edge_lengths(self.graph)  # Add edge lengths in meters
        
    def load_emergency_services(self, filename=r'F:\AI\Project\Disaster-Response-System\data\cached_networks\emergency_services.csv'):
        """Load emergency services into graph"""
        services_df = pd.read_csv(filename)
        
        for _, row in services_df.iterrows():
            # Find nearest node in road network
            nearest_node = ox.distance.nearest_nodes(
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
            
    def load_shelters(self, filename=r'F:\AI\Project\Disaster-Response-System\data\cached_networks\shelters.csv'):
        """Load shelter locations into graph"""
        shelters_df = pd.read_csv(filename)
        
        for _, row in shelters_df.iterrows():
            nearest_node = ox.distance.nearest_nodes(
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
        """
        Add a danger zone. If the new coordinate overlaps with an existing danger zone,
        extend the radius of the existing zone to include the new coordinate.
        """
        def distance(lat1, lon1, lat2, lon2):
            # Calculate distance in meters between two lat/lon points
            R = 6371000  # Earth's radius in meters
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)
            a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
            return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Check if the new danger zone overlaps with any existing ones
        for existing_zone in list(self.danger_zones):
            existing_lat, existing_lon, existing_radius = existing_zone
            dist_to_center = distance(lat, lon, existing_lat, existing_lon)
            if dist_to_center <= existing_radius:
                # Extend the radius of the existing zone if the new point is outside its current boundary
                new_radius = max(existing_radius, dist_to_center + radius)
                self.danger_zones.remove(existing_zone)
                self.danger_zones.add((existing_lat, existing_lon, new_radius))
                return

        # If no overlap, add the new danger zone
        self.danger_zones.add((lat, lon, radius))
    
    def find_safe_path(self, start_lat, start_lon, end_lat, end_lon):
        """Find safest path between two points"""
        # Get nearest nodes to start and end points
        start_node = ox.distance.nearest_nodes(self.graph, start_lon, start_lat)
        end_node = ox.distance.nearest_nodes(self.graph, end_lon, end_lat)

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
        m = folium.Map(location=[24.8700, 67.0200], zoom_start=13)
        
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
        for lat, lon, radius in self.danger_zones:
            folium.Circle(
                location=(lat, lon),
                radius=radius,  # Adjust the radius as needed
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.5  # Semi-transparent
            ).add_to(m)
        
        # Save the map to an HTML file
        m.save(save_path)
        print(f"Graph visualization saved to {save_path}")
    
    def find_closest_node(self, lat, lon):
        """Find the closest node in the graph to a given latitude and longitude"""
        return ox.distance.nearest_nodes(self.graph, lon, lat)