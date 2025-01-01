import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QStackedLayout, QHBoxLayout, QFrame)
from PyQt6.QtCore import Qt, pyqtSlot, QObject, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
import folium
import io
from graph_structure import DisasterGraph  # Import the DisasterGraph class
from a_star_pathfinding import PathFinder, find_nearest_service  # Correctly import PathFinder and find_nearest_service

class WelcomePage(QWidget):
    def __init__(self, stacked_layout, parent=None):
        super().__init__(parent)
        self.stacked_layout = stacked_layout
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # System name label
        system_name = QLabel("Disaster Response System")
        system_name.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        system_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(system_name)

        # Start button
        start_button = QPushButton("Start")
        start_button.setFont(QFont("Arial", 18))
        start_button.setStyleSheet("background-color: green; color: white; padding: 20px 40px;")
        start_button.clicked.connect(self.on_start_button_clicked)
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def on_start_button_clicked(self):
        self.stacked_layout.setCurrentIndex(1)

class SelectionPage(QWidget):
    def __init__(self, stacked_layout, parent=None):
        super().__init__(parent)
        self.stacked_layout = stacked_layout
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Selection label
        selection_label = QLabel("Select Your Role")
        selection_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(selection_label)

        # Rescue team button
        rescue_button = QPushButton("Rescue Team")
        rescue_button.setFont(QFont("Arial", 18))
        rescue_button.setStyleSheet("background-color: green; color: white; padding: 20px 40px;")
        rescue_button.clicked.connect(self.on_rescue_button_clicked)
        layout.addWidget(rescue_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Affected victim button
        victim_button = QPushButton("Affected Victim")
        victim_button.setFont(QFont("Arial", 18))
        victim_button.setStyleSheet("background-color: green; color: white; padding: 20px 40px;")
        victim_button.clicked.connect(self.on_victim_button_clicked)
        layout.addWidget(victim_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def on_rescue_button_clicked(self):
        self.stacked_layout.setCurrentIndex(2)

    def on_victim_button_clicked(self):
        print("Affected Victim selected")
        # Add logic to handle affected victim selection

class MapPage(QWidget):
    coordinatesUpdated = pyqtSignal(str)

    def __init__(self, disaster_graph, parent=None):
        super().__init__(parent)
        self.disaster_graph = disaster_graph
        self.pathfinder = PathFinder(disaster_graph)
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        # Create a QWebEngineView to display the map
        self.map_view = QWebEngineView()
        layout.addWidget(self.map_view)

        # Create a side panel
        self.side_panel = QFrame()
        self.side_panel.setFrameShape(QFrame.Shape.StyledPanel)
        self.side_panel.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.side_panel_layout = QVBoxLayout()
        self.side_panel.setLayout(self.side_panel_layout)

        # Add a label to display coordinates
        self.coordinates_label = QLabel("Disaster Coordinates:")
        self.coordinates_label.setFont(QFont("Arial", 16))
        self.coordinates_label.setStyleSheet("color: #333; padding: 10px;")
        self.side_panel_layout.addWidget(self.coordinates_label)

        # Add labels for nearest services
        self.nearest_services_label = QLabel("")
        self.nearest_services_label.setFont(QFont("Arial", 14))
        self.nearest_services_label.setStyleSheet("color: #333; padding: 10px;")
        self.side_panel_layout.addWidget(self.nearest_services_label)

        layout.addWidget(self.side_panel)

        self.setLayout(layout)
        self.update_map()

    def update_map(self, paths=None):
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

        # Add danger zones to the map with click handlers
        for lat, lon, radius in self.disaster_graph.danger_zones:
            circle = folium.Circle(
                location=(lat, lon),
                radius=radius,  # Adjust the radius as needed
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.5  # Semi-transparent
            )
            circle.add_child(folium.Popup(f"Coordinates: {lat}, {lon}"))
            circle.add_to(m)

        # Draw paths if provided
        if paths:
            for path in paths:
                folium.PolyLine(path, color="blue", weight=2.5, opacity=1).add_to(m)

        # Save the map to a temporary HTML file
        data = io.BytesIO()
        m.save(data, close_file=False)
        self.map_view.setHtml(data.getvalue().decode())

    def update_disaster_info(self, lat, lon):
        coordinates = f"{lat}, {lon}"
        current_text = self.coordinates_label.text()
        new_text = current_text + "\n" + coordinates
        self.coordinates_label.setText(new_text)

        # Find nearest services
        hospital_path, hospital_distance, hospital_name = find_nearest_service(self.disaster_graph, self.pathfinder, lat, lon, 'hospital')
        fire_station_path, fire_station_distance, fire_station_name = find_nearest_service(self.disaster_graph, self.pathfinder, lat, lon, 'fire_station')
        police_station_path, police_station_distance, police_station_name = find_nearest_service(self.disaster_graph, self.pathfinder, lat, lon, 'police_station')

        # Handle cases where no path is found
        if hospital_distance is None:
            hospital_distance = float('inf')
            hospital_name = "No path found"
        if fire_station_distance is None:
            fire_station_distance = float('inf')
            fire_station_name = "No path found"
        if police_station_distance is None:
            police_station_distance = float('inf')
            police_station_name = "No path found"

        # Update the nearest services label
        nearest_services_text = f"Nearest Hospital: {hospital_name} ({hospital_distance/1000:.2f} km)\n"
        nearest_services_text += f"Nearest Fire Station: {fire_station_name} ({fire_station_distance/1000:.2f} km)\n"
        nearest_services_text += f"Nearest Police Station: {police_station_name} ({police_station_distance/1000:.2f} km)"
        self.nearest_services_label.setText(nearest_services_text)

        # Update the map with paths
        paths = []
        if hospital_path:
            paths.append(hospital_path)
        if fire_station_path:
            paths.append(fire_station_path)
        if police_station_path:
            paths.append(police_station_path)
        self.update_map(paths)

class DisasterResponseUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Disaster Response System')
        self.setGeometry(100, 100, 1000, 600)

        # Create stacked layout
        self.stacked_layout = QStackedLayout()

        # Initialize the disaster graph
        self.disaster_graph = DisasterGraph()
        self.disaster_graph.build_from_osm("Saddar, Karachi, Pakistan")
        self.disaster_graph.load_emergency_services()
        self.disaster_graph.load_shelters()

        # Add some sample danger zones
        self.disaster_graph.add_danger_zone(24.8607, 67.0011, 200)  # 200m radius
        self.disaster_graph.add_danger_zone(24.8700, 67.0200, 150)  # 150m radius
        self.disaster_graph.add_danger_zone(24.8750, 67.0100, 300)  # 300m radius

        # Add welcome page
        self.welcome_page = WelcomePage(self.stacked_layout)
        self.stacked_layout.addWidget(self.welcome_page)

        # Add selection page
        self.selection_page = SelectionPage(self.stacked_layout)
        self.stacked_layout.addWidget(self.selection_page)

        # Add map page
        self.map_page = MapPage(self.disaster_graph)
        self.stacked_layout.addWidget(self.map_page)

        # Set the layout
        container = QWidget()
        container.setLayout(self.stacked_layout)
        self.setCentralWidget(container)

        # Hardcoded disaster zone coordinates
        disaster_lat, disaster_lon = 24.8750, 67.0100
        self.map_page.update_disaster_info(disaster_lat, disaster_lon)

def main():
    app = QApplication(sys.argv)
    ui = DisasterResponseUI()
    ui.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()