import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QComboBox, 
                            QTableWidget, QTableWidgetItem, QGroupBox, QDialog,
                            QFormLayout, QDoubleSpinBox, QSpinBox, QTextEdit)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QIcon, QFont
import folium
import io
import numpy as np
from typing import List, Tuple, Dict
import heapq
from graph_structure import DisasterGraph  # Import the DisasterGraph class

class ResourceAllocation:
    def __init__(self, emergency_services, danger_zones):
        self.emergency_services = emergency_services
        self.danger_zones = danger_zones
        
    def calculate_utility(self, service, zone):
        """Calculate utility based on distance and service capacity"""
        distance = self.calculate_distance(
            service['location'],
            (zone['latitude'], zone['longitude'])
        )
        return (1000 / distance) * service.get('capacity', 1)
    
    def allocate_resources(self):
        """Implement non-zero sum game theory for resource allocation"""
        allocations = {}
        available_services = set(self.emergency_services.keys())
        
        # Sort danger zones by severity
        sorted_zones = sorted(
            self.danger_zones.items(), 
            key=lambda x: x[1]['severity'], 
            reverse=True
        )
        
        for zone_id, zone in sorted_zones:
            zone_allocations = {}
            utilities = {
                service_id: self.calculate_utility(service, zone)
                for service_id, service in self.emergency_services.items()
                if service_id in available_services
            }
            
            # Allocate based on Nash equilibrium
            while utilities and len(zone_allocations) < 3:  # Limit to 3 services per zone
                best_service = max(utilities.items(), key=lambda x: x[1])[0]
                zone_allocations[best_service] = utilities[best_service]
                available_services.remove(best_service)
                utilities.pop(best_service)
            
            allocations[zone_id] = zone_allocations
            
        return allocations

class DetailedInfoDialog(QDialog):
    def __init__(self, location_data, parent=None):
        super().__init__(parent)
        self.location_data = location_data
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Create info text
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        
        # Format location data
        formatted_info = self.format_location_info()
        info_text.setText(formatted_info)
        
        layout.addWidget(info_text)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        self.setWindowTitle("Location Details")
        self.setMinimumWidth(400)

    def format_location_info(self):
        info = []
        for key, value in self.location_data.items():
            if key == 'location':
                info.append(f"Location: {value[0]:.6f}, {value[1]:.6f}")
            else:
                info.append(f"{key.title()}: {value}")
        return "\n".join(info)

class AddDangerZoneDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        layout = QFormLayout()
        
        self.lat_input = QDoubleSpinBox()
        self.lat_input.setRange(-90, 90)
        self.lat_input.setDecimals(6)
        self.lat_input.setValue(24.8607)
        
        self.lon_input = QDoubleSpinBox()
        self.lon_input.setRange(-180, 180)
        self.lon_input.setDecimals(6)
        self.lon_input.setValue(67.0011)
        
        self.radius_input = QSpinBox()
        self.radius_input.setRange(100, 5000)
        self.radius_input.setValue(500)
        
        self.severity_input = QSpinBox()
        self.severity_input.setRange(1, 10)
        self.severity_input.setValue(5)
        
        layout.addRow("Latitude:", self.lat_input)
        layout.addRow("Longitude:", self.lon_input)
        layout.addRow("Radius (m):", self.radius_input)
        layout.addRow("Severity (1-10):", self.severity_input)
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("Add")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addRow(buttons)
        
        self.setLayout(layout)
        self.setWindowTitle("Add Danger Zone")

class DisasterResponseUI(QMainWindow):
    def __init__(self, disaster_graph):
        super().__init__()
        self.disaster_graph = disaster_graph
        self.current_routes = []
        self.selected_location = None
        self.initUI()

    # ... (previous UI initialization code remains the same)
    def initUI(self):
        self.setWindowTitle('Disaster Response System')
        self.setGeometry(100, 100, 800, 600)

        # Create main layout
        main_layout = QVBoxLayout()

        # Add widgets to the layout
        self.map_view = QWebEngineView()
        main_layout.addWidget(self.map_view)

        self.update_map()

        # Set the layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def update_map(self):
        # Generate the map
        m = folium.Map(location=[24.8607, 67.0011], zoom_start=13)

        # Add emergency services to the map
        for node, data in self.disaster_graph.emergency_services.items():
            folium.Marker(
                location=data['location'],
                popup=f"{data['name']} ({data['type']})",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)

        # Add shelters to the map
        for node, data in self.disaster_graph.shelters.items():
            folium.Marker(
                location=data['location'],
                popup=f"{data['name']} (Capacity: {data['capacity']})",
                icon=folium.Icon(color='green', icon='home')
            ).add_to(m)

        # Add danger zones to the map as semi-transparent red circles
        for lat, lon, radius in self.disaster_graph.danger_zones:
            folium.Circle(
                location=(lat, lon),
                radius=radius,  # Adjust the radius as needed
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.5  # Semi-transparent
            ).add_to(m)

        # Save the map to a temporary HTML file
        data = io.BytesIO()
        m.save(data, close_file=False)
        self.map_view.setHtml(data.getvalue().decode())


    def createControlPanel(self):
        # ... (previous control panel code)
        
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Add Route Options
        route_options = QGroupBox("Route Options")
        route_layout = QVBoxLayout()
        
        self.route_algorithm = QComboBox()
        self.route_algorithm.addItems(['A* Algorithm', 'Dijkstra\'s Algorithm'])
        route_layout.addWidget(QLabel("Routing Algorithm:"))
        route_layout.addWidget(self.route_algorithm)
        
        self.route_count = QSpinBox()
        self.route_count.setRange(1, 5)
        self.route_count.setValue(3)
        route_layout.addWidget(QLabel("Number of Alternative Routes:"))
        route_layout.addWidget(self.route_count)
        
        route_options.setLayout(route_layout)
        layout.addWidget(route_options)
        
        return panel

    def findAlternativeRoutes(self, start, end, num_routes=3):
        """Find multiple alternative routes using A* algorithm"""
        routes = []
        blocked_edges = set()
        
        for _ in range(num_routes):
            # Find a new route
            path = self.disaster_graph.a_star_search(start, end, blocked_edges)
            if not path:
                break
                
            routes.append(path)
            
            # Block edges in this path to force finding alternative routes
            for i in range(len(path) - 1):
                blocked_edges.add((path[i], path[i + 1]))
                blocked_edges.add((path[i + 1], path[i]))
        
        return routes

    def showLocationDetails(self, location_id, location_type):
        """Show detailed information about selected location"""
        if location_type == 'service':
            data = self.disaster_graph.emergency_services.get(location_id)
        elif location_type == 'shelter':
            data = self.disaster_graph.shelters.get(location_id)
        else:
            return
            
        if data:
            dialog = DetailedInfoDialog(data, self)
            dialog.exec()

    def updateMap(self):
        """Enhanced map update with multiple routes and better visualization"""
        m = folium.Map(location=[24.8607, 67.0011], zoom_start=12)
        
        # Add markers and danger zones as before
        
        # Add multiple routes if available
        colors = ['blue', 'green', 'purple', 'orange', 'brown']
        for i, route in enumerate(self.current_routes):
            if i >= len(colors):
                break
                
            route_coords = [(self.disaster_graph.graph.nodes[node]['y'],
                            self.disaster_graph.graph.nodes[node]['x'])
                           for node in route]
            
            folium.PolyLine(
                route_coords,
                weight=3,
                color=colors[i],
                opacity=0.8,
                popup=f'Route {i+1}'
            ).add_to(m)
        
        # Update the web view
        data = io.BytesIO()
        m.save(data, close_file=False)
        self.web_view.setHtml(data.getvalue().decode())

    def calculateRoute(self):
        """Calculate multiple routes between selected points"""
        if not hasattr(self, 'start_point') or not hasattr(self, 'end_point'):
            # Show error message
            return
            
        num_routes = self.route_count.value()
        self.current_routes = self.findAlternativeRoutes(
            self.start_point,
            self.end_point,
            num_routes
        )
        
        self.updateMap()
        self.updateRouteStats()

    def addDangerZone(self):
        """Add new danger zone with severity"""
        dialog = AddDangerZoneDialog(self)
        if dialog.exec():
            lat = dialog.lat_input.value()
            lon = dialog.lon_input.value()
            radius = dialog.radius_input.value()
            severity = dialog.severity_input.value()
            
            self.disaster_graph.add_danger_zone(lat, lon, radius, severity)
            self.updateMap()
            self.updateStats()
            
            # Recalculate resource allocation
            self.updateResourceAllocation()

    def updateResourceAllocation(self):
        """Update resource allocation based on game theory"""
        resource_allocator = ResourceAllocation(
            self.disaster_graph.emergency_services,
            self.disaster_graph.danger_zones
        )
        
        allocations = resource_allocator.allocate_resources()
        
        # Update UI with new allocations
        self.displayResourceAllocations(allocations)

    def displayResourceAllocations(self, allocations):
        """Display resource allocations in the UI"""
        # Create or update allocation table
        if not hasattr(self, 'allocation_table'):
            self.allocation_table = QTableWidget()
            self.info_panel_layout.addWidget(self.allocation_table)
            
        self.allocation_table.setRowCount(len(allocations))
        self.allocation_table.setColumnCount(2)
        self.allocation_table.setHorizontalHeaderLabels(['Danger Zone', 'Assigned Services'])
        
        for i, (zone_id, services) in enumerate(allocations.items()):
            self.allocation_table.setItem(i, 0, QTableWidgetItem(f"Zone {zone_id}"))
            services_text = ", ".join([
                f"{self.disaster_graph.emergency_services[service_id]['name']}"
                for service_id in services
            ])
            self.allocation_table.setItem(i, 1, QTableWidgetItem(services_text))

def main():
    # Initialize the disaster graph
    disaster_graph = DisasterGraph()
    
    # Build the graph and load data
    disaster_graph.build_from_osm("Saddar, Karachi, Pakistan")
    disaster_graph.load_emergency_services()
    disaster_graph.load_shelters()
    
    # Create and show the UI
    app = QApplication(sys.argv)
    disaster_graph = DisasterGraph()
    disaster_graph.build_from_osm("Saddar, Karachi, Pakistan")
    disaster_graph.load_emergency_services()
    disaster_graph.load_shelters()
    ui = DisasterResponseUI(disaster_graph)
    ui.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()