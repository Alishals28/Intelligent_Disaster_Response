from heapq import heappush, heappop
from math import sqrt, radians, sin, cos, asin
import networkx as nx
import osmnx as ox
from graph_structure import DisasterGraph

class PathFinder:
    def __init__(self, disaster_graph):
        self.graph = disaster_graph.graph
        self.shelters = disaster_graph.shelters
        
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        # Radius of earth in kilometers
        r = 6371
        return c * r * 1000  # Convert to meters

    def heuristic(self, node_a, node_b):
        """
        Calculate the Euclidean distance as the heuristic.
        """
        coord_a = (self.graph.nodes[node_a]['y'], self.graph.nodes[node_a]['x'])
        coord_b = (self.graph.nodes[node_b]['y'], self.graph.nodes[node_b]['x'])
        return sqrt((coord_a[0] - coord_b[0])**2 + (coord_a[1] - coord_b[1])**2)

    def a_star(self, start, goal):
        """
        Perform the A* algorithm to find the quickest path.

        Parameters:
            start: The starting node.
            goal: The goal node.

        Returns:
            path: A list of nodes representing the path from start to goal.
        """
        open_set = []
        heappush(open_set, (0, start))

        came_from = {}
        g_score = {node: float('inf') for node in self.graph.nodes}
        g_score[start] = 0

        f_score = {node: float('inf') for node in self.graph.nodes}
        f_score[start] = self.heuristic(start, goal)

        while open_set:
            current = heappop(open_set)[1]

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path

            for neighbor in self.graph.neighbors(current):
                tentative_g_score = g_score[current] + self.graph.edges[current, neighbor, 0]['length']

                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, goal)
                    heappush(open_set, (f_score[neighbor], neighbor))

        return None

    def get_path_coordinates(self, path):
        """
        Convert path node IDs to list of coordinates for visualization
        """
        if not path:
            return []
            
        return [(self.graph.nodes[node]['y'], self.graph.nodes[node]['x']) 
                for node in path]

    def calculate_path_distance(self, path):
        """
        Calculate the total distance of the path in meters.
        """
        if not path:
            return 0
        
        total_distance = 0
        for i in range(len(path) - 1):
            node_a = path[i]
            node_b = path[i + 1]
            total_distance += self.graph.edges[node_a, node_b, 0]['length']
        
        return total_distance

def find_nearest_shelter(disaster_graph, pathfinder, danger_zone_lat, danger_zone_lon):
    nearest_shelter_node = None
    nearest_shelter_distance = float('inf')
    for node, data in disaster_graph.shelters.items():
        distance = pathfinder.haversine_distance(danger_zone_lat, danger_zone_lon, data['location'][0], data['location'][1])
        if distance < nearest_shelter_distance:
            nearest_shelter_distance = distance
            nearest_shelter_node = node

    if nearest_shelter_node is None:
        print("No shelter found.")
        return None, None, None

    start_node = ox.nearest_nodes(disaster_graph.graph, danger_zone_lon, danger_zone_lat)
    goal_node = nearest_shelter_node

    path = pathfinder.a_star(start_node, goal_node)
    if path:
        path_coords = pathfinder.get_path_coordinates(path)
        total_distance = pathfinder.calculate_path_distance(path)
        return path_coords, total_distance, disaster_graph.shelters[nearest_shelter_node]['name']
    else:
        print("No path found to the nearest shelter.")
        return None, None, None

def main():
    # Initialize the disaster graph
    disaster_graph = DisasterGraph()
    disaster_graph.build_from_osm("Saddar, Karachi, Pakistan")
    disaster_graph.load_emergency_services()
    disaster_graph.load_shelters()

    # Add a sample danger zone
    danger_zone_lat, danger_zone_lon = 24.8750, 67.0100
    disaster_graph.add_danger_zone(danger_zone_lat, danger_zone_lon, 200)  # 200m radius

    # Initialize the pathfinder
    pathfinder = PathFinder(disaster_graph)

    # Find the nearest shelter
    shelter_path, shelter_distance, shelter_name = find_nearest_shelter(disaster_graph, pathfinder, danger_zone_lat, danger_zone_lon)
    if shelter_path:
        print("Path to nearest shelter found!")
        print(f"Disaster Zone: ({danger_zone_lat}, {danger_zone_lon})")
        print("Path coordinates to shelter:")
        for coord in shelter_path:
            print(coord)
        print(f"Total distance to shelter: {shelter_distance/1000:.2f} km")
        print(f"Nearest shelter: {shelter_name}")

if __name__ == "__main__":
    main()