from heapq import heappush, heappop
from math import sqrt
from graph_structure import DisasterGraph

def heuristic(node_a, node_b):
    """
    Calculate the Euclidean distance as the heuristic.
    """
    return sqrt((node_a[0] - node_b[0])**2 + (node_a[1] - node_b[1])**2)

def a_star(graph, start, goal):
    """
    Perform the A* algorithm to find the quickest path.

    Parameters:
        graph: The graph representation (NetworkX Graph).
        start: The starting node.
        goal: The goal node.

    Returns:
        path: A list of nodes representing the path from start to goal.
    """
    open_set = []
    heappush(open_set, (0, start))

    came_from = {}
    g_score = {node: float('inf') for node in graph.nodes}
    g_score[start] = 0

    f_score = {node: float('inf') for node in graph.nodes}
    f_score[start] = heuristic(graph.nodes[start]['location'], graph.nodes[goal]['location'])

    while open_set:
        _, current = heappop(open_set)

        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]

        for neighbor in graph.neighbors(current):
            tentative_g_score = g_score[current] + graph[current][neighbor].get('weight', 1)

            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(graph.nodes[neighbor]['location'], graph.nodes[goal]['location'])
                heappush(open_set, (f_score[neighbor], neighbor))

    return None  # No path found

def main():
    # Initialize DisasterGraph
    disaster_graph = DisasterGraph()

    # Build the graph from OpenStreetMap
    print("Building graph from OSM data...")
    disaster_graph.build_from_osm("Karachi", "Pakistan")

    # Load data
    print("Loading emergency services...")
    disaster_graph.load_emergency_services()
    print("Loading shelters...")
    disaster_graph.load_shelters()

    # Define start (emergency service) and end (disaster location)
    start = (24.8607, 67.0011)  # Example location for emergency service
    goal = (24.8700, 67.0200)   # Example location for disaster zone

    # Find the closest nodes in the graph
    start_node = disaster_graph.find_closest_node(start[0], start[1])
    goal_node = disaster_graph.find_closest_node(goal[0], goal[1])

    print(f"Start node: {start_node}, Goal node: {goal_node}")

    # Perform A* algorithm
    print("Finding quickest path using A*...")
    path = a_star(disaster_graph.graph, start_node, goal_node)

    if path:
        print("Path found:", path)
    else:
        print("No path found!")

if __name__ == "__main__":
    main()
