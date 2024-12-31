from graph_structure import DisasterGraph
import folium

def test_graph_functionality():
    # Initialize graph
    disaster_graph = DisasterGraph()
    
    # Build graph for Karachi
    print("Building graph from OSM data...")
    disaster_graph.build_from_osm("Saddar, Karachi, Pakistan")
    
    # Load emergency services and shelters
    print("Loading emergency services...")
    disaster_graph.load_emergency_services()
    print(disaster_graph.emergency_services)  # debug
    print("Loading shelters...")
    disaster_graph.load_shelters()
    print(disaster_graph.shelters)  # debug

    # Add sample danger zones with the new functionality
    print("Adding danger zones...")
    disaster_graph.add_danger_zone(24.8607, 67.0011, 200)  # 200m radius
    disaster_graph.add_danger_zone(24.8700, 67.0200, 150)  # 150m radius
    disaster_graph.add_danger_zone(24.8750, 67.0100, 300)  # 300m radius

    # Print the number of danger zones
    print(f"Number of danger zones: {len(disaster_graph.danger_zones)}")

    # Test path finding
    print("Testing safe path finding...")
    start = (24.8607, 67.0011)  # Saddar area
    end = (24.8823, 67.0337)    # Gulshan-e-Iqbal

    path = disaster_graph.find_safe_path(
        start[0], start[1],
        end[0], end[1]
    )
    
    # Create a folium map
    m = folium.Map(location=[24.8607, 67.0011], zoom_start=13)

    # Add shelters to the map
    print("Adding shelters to the map...")
    for shelter in disaster_graph.shelters.values():
        folium.Marker(
            location=shelter['location'],
            icon=folium.Icon(color='green', icon='home'),
            popup=f"Shelter: {shelter['name']}"
        ).add_to(m)

    # Add emergency services to the map
    print("Adding emergency services to the map...")
    for service in disaster_graph.emergency_services.values():
        folium.Marker(
            location=service['location'],
            icon=folium.Icon(color='red', icon='plus-sign'),
            popup=f"Service: {service['name']}"
        ).add_to(m)

    # Add danger zones to the map
    print("Adding danger zones to the map...")
    for lat, lon, radius in disaster_graph.danger_zones:
        folium.Circle(
            location=(lat, lon),
            radius=radius,  # Dynamically adjusted radius
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.2
        ).add_to(m)

    # Add the safe path to the map if found
    if path:
        print("Safe path found!")
        path_coords = [(disaster_graph.graph.nodes[node]['y'], 
                       disaster_graph.graph.nodes[node]['x']) 
                      for node in path]

        folium.PolyLine(
            path_coords,
            weight=3,
            color='blue',
            opacity=0.8
        ).add_to(m)

        print("Safe path added to the map.")
    else:
        print("No safe path found!")

    # Save the map
    m.save('test_path.html')
    print("Map visualization saved to test_path.html")

if __name__ == "__main__":
    test_graph_functionality()
