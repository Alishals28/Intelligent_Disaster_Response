import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QStackedLayout, QHBoxLayout, QFrame, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage  # For custom page
import folium
import osmnx as ox
import io
from graph_structure import DisasterGraph  # Import the DisasterGraph class
from a_star_pathfinding import PathFinder, find_nearest_service  # Correctly import PathFinder and find_nearest_service
from shelter import find_nearest_shelter 
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPixmap


# Custom QWebEnginePage class
class CustomWebEnginePage(QWebEnginePage):
    linkClicked = pyqtSignal(dict)
    mapClicked = pyqtSignal(float, float)  # New signal for map clicks

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if message.startswith("Coordinates:"):
            try:
                # Parse coordinates from the message
                lat, lon = map(float, message.replace("Coordinates:", "").strip().split(","))
                self.mapClicked.emit(lat, lon)
            except:
                print("Error parsing coordinates")

    def acceptNavigationRequest(self, url, nav_type, isMainFrame):
        url_str = url.toString()
        if url_str.startswith("info://"):
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(url_str)
            query = parse_qs(parsed_url.query)

            lat = float(query.get("lat", [0])[0])
            lon = float(query.get("lon", [0])[0])
            radius = float(query.get("radius", [0])[0])

            self.linkClicked.emit({"lat": lat, "lon": lon, "radius": radius})
            return False

        return super().acceptNavigationRequest(url, nav_type, isMainFrame)

class WelcomePage(QWidget):
    def __init__(self, stacked_layout, parent=None):
        super().__init__(parent)
        self.stacked_layout = stacked_layout
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Background label
        self.background_label = QLabel(self)
        pixmap = QPixmap(r"F:\AI\Project\Disaster-Response-System\src\graph\rescue.png") 
        if pixmap.isNull():
            print("Failed to load image.") 
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.resize(self.size())  # Resize the background to match the window
        self.background_label.setGeometry(self.rect())
        self.background_label.lower()

        # System name label
        system_name = QLabel("Disaster Response System")
        system_name.setFont(QFont("Arial", 40, QFont.Weight.Bold))
        system_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        system_name.setStyleSheet("color: white;")
        layout.addWidget(system_name)

        # Start button
        start_button = QPushButton("Start")
        start_button.setFont(QFont("Arial", 18))
        start_button.setStyleSheet("background-color: green; color: white; padding: 20px 40px;")
        start_button.clicked.connect(self.on_start_button_clicked)
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def resizeEvent(self, event):
        """Update background label size on window resize."""
        self.background_label.setGeometry(self.rect())
        super().resizeEvent(event)

    def on_start_button_clicked(self):
        self.stacked_layout.setCurrentIndex(1)
    
class SelectionPage(QWidget):
    def __init__(self, stacked_layout, main_window, parent=None):
        super().__init__(parent)
        self.stacked_layout = stacked_layout
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Background label
        self.background_label = QLabel(self)
        pixmap = QPixmap(r"F:\AI\Project\Disaster-Response-System\src\graph\2.png") 
        if pixmap.isNull():
            print("Failed to load image.") 
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.resize(self.size())  # Resize the background to match the window
        self.background_label.setGeometry(self.rect())
        self.background_label.lower()

        # Selection label
        selection_label = QLabel("You're using the app as a")
        selection_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        selection_label.setStyleSheet("color: white;")
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

        # Back button
        back_button = QPushButton("Back")
        back_button.setFont(QFont("Arial", 18))
        back_button.setStyleSheet("background-color: red; color: white; padding: 20px 40px;")
        back_button.clicked.connect(self.on_back_button_clicked)
        layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def resizeEvent(self, event):
        """Update background label size on window resize."""
        self.background_label.setGeometry(self.rect())
        super().resizeEvent(event)

    def on_rescue_button_clicked(self):
        self.stacked_layout.setCurrentIndex(2)
        disaster_lat, disaster_lon = 24.8700, 67.0200
        self.main_window.map_page.update_disaster_info(disaster_lat, disaster_lon)

    def on_victim_button_clicked(self):
        self.stacked_layout.setCurrentIndex(3)
        disaster_lat, disaster_lon = 24.8700, 67.0200
        self.main_window.user_map_page.update_disaster_info(disaster_lat, disaster_lon, role='victim')

    def on_back_button_clicked(self):
        self.stacked_layout.setCurrentIndex(0)


class MapPage(QWidget):
    coordinatesUpdated = pyqtSignal(str)

    def __init__(self, stacked_layout, disaster_graph, parent=None):
        super().__init__(parent)
        self.stacked_layout = stacked_layout
        self.disaster_graph = disaster_graph
        self.pathfinder = PathFinder(disaster_graph)
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        # Create a QWebEngineView to display the map
        self.map_view = QWebEngineView()
        self.page = CustomWebEnginePage(self.map_view)
        self.page.linkClicked.connect(self.on_link_clicked)
        self.page.mapClicked.connect(self.on_map_clicked)  # Connect new signal
        self.map_view.setPage(self.page)
        layout.addWidget(self.map_view)

        # Create a side panel
        self.side_panel = QFrame()
        self.side_panel.setFrameShape(QFrame.Shape.StyledPanel)
        self.side_panel.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.side_panel_layout = QVBoxLayout()
        self.side_panel.setLayout(self.side_panel_layout)

        # Create coordinate input section
        coord_layout = QHBoxLayout()
        self.coordinates_label = QLabel("Disaster Coordinates:")
        self.coordinates_label.setFont(QFont("Arial", 16))
        self.coordinates_label.setStyleSheet("color: #333; padding: 10px;")
        coord_layout.addWidget(self.coordinates_label)
        
        # Add text box for coordinates
        self.coord_input = QLineEdit()
        self.coord_input.setPlaceholderText("lat, lon")
        self.coord_input.setFont(QFont("Arial", 14))
        self.coord_input.setStyleSheet("padding: 5px; color: black;")
        coord_layout.addWidget(self.coord_input)
        
        # Add find button
        find_button = QPushButton("Find Services")
        find_button.setFont(QFont("Arial", 14))
        find_button.setStyleSheet("background-color: #007bff; color: white; padding: 5px;")
        find_button.clicked.connect(self.on_find_button_clicked)
        coord_layout.addWidget(find_button)
        
        self.side_panel_layout.addLayout(coord_layout)

        # Add labels for nearest services
        self.nearest_services_label = QLabel("")
        self.nearest_services_label.setFont(QFont("Arial", 14))
        self.nearest_services_label.setStyleSheet("color: #333; padding: 10px;")
        self.side_panel_layout.addWidget(self.nearest_services_label)

        # Create a label for the emergency message
        self.emergency_message_label = QLabel("")
        self.emergency_message_label.setFont(QFont("Arial", 14))
        self.emergency_message_label.setStyleSheet("color: red; padding: 10px;")
        self.side_panel_layout.addWidget(self.emergency_message_label)

        # Add a call button
        self.call_button = QPushButton()
        self.call_button.setFont(QFont("Arial", 14))
        self.call_button.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")
        self.call_button.setIcon(QIcon("C:/Users/B.J COMP/Documents/3rd SEM/AI Project/Intelligent_Disaster_Response/src/graph/image.png"))
        self.call_button.setIconSize(QSize(40, 40))
        self.call_button.setText("Call for Help")

        # Back button
        back_button = QPushButton("Back")
        back_button.setFont(QFont("Arial", 18))
        back_button.setStyleSheet("background-color: red; color: white; padding: 20px 40px;")
        back_button.clicked.connect(self.on_back_button_clicked)
        self.side_panel_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Store current coordinates
        self.current_lat = None
        self.current_lon = None
        self.current_role = None
        
        layout.addWidget(self.side_panel)
        self.setLayout(layout)
        self.update_map()

    def on_back_button_clicked(self):
        self.stacked_layout.setCurrentIndex(1)

    def update_map(self, paths=None):
        m = folium.Map(location=[24.8700, 67.0200], zoom_start=13)

        # Add click event listener to the map
        m.add_child(folium.ClickForMarker(popup="Selected Location"))
        
        # Add JavaScript to capture clicks
        m.get_root().html.add_child(folium.Element("""
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                setTimeout(function() {
                    var map = document.querySelector('#map');
                    map.addEventListener('click', function(e) {
                        var coordinates = e.latlng;
                        console.log("Coordinates:" + coordinates.lat + "," + coordinates.lng);
                    });
                }, 1000);
            });
            </script>
        """))

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

        # Add danger zones to the map
        for lat, lon, radius in self.disaster_graph.danger_zones:
            circle = folium.Circle(
                location=(lat, lon),
                radius=radius,
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.5,
                popup=f'Coordinates: {lat}, {lon}'
            ).add_to(m)

        # Draw paths if provided
        if paths:
            for path in paths:
                if path:
                    folium.PolyLine(path, color="blue", weight=2.5, opacity=1).add_to(m)

        data = io.BytesIO()
        m.save(data, close_file=False)
        self.map_view.setHtml(data.getvalue().decode())

    def on_map_clicked(self, lat, lon):
        """Handle map click events"""
        self.coord_input.setText(f"{lat}, {lon}")

    def on_find_button_clicked(self):
        """Handle find button clicks"""
        try:
            lat, lon = map(float, self.coord_input.text().split(","))
            self.update_disaster_info(lat, lon, self.role if hasattr(self, 'role') else None)
        except ValueError:
            self.emergency_message_label.setText("Invalid coordinates! Please use format: lat, lon")

    def update_disaster_info(self, lat, lon, role=None):
        self.role = role  # Store the role
        if role == 'victim':
            # Find nearest shelter
            shelter_path, shelter_distance, shelter_name = find_nearest_shelter(
                self.disaster_graph, self.pathfinder, lat, lon
            )

            if shelter_path:
                self.nearest_services_label.setText(
                    f"Nearest Shelter: {shelter_name}\nDistance: {shelter_distance / 1000:.2f} km"
                )
                path_coords = shelter_path
                self.update_map([path_coords])
            else:
                self.nearest_services_label.setText("No shelter found.")
                self.update_map()

            self.emergency_message_label.setText("Call shelter for assistance.")

        else:
            # Find nearest emergency services
            services = ['police_station','hospital','fire_station']
            paths = []
            nearest_services_text = ""

            for service_type in services:
                service_path, service_distance, service_name = find_nearest_service(
                    self.disaster_graph, self.pathfinder, lat, lon, service_type
                )
                if service_path:
                    paths.append(service_path)
                    nearest_services_text += f"Name: {service_name}\n"
                    nearest_services_text += f"Distance: {service_distance / 1000:.2f} km\n\n"
                else:
                    nearest_services_text += f"No {service_type.replace('_', ' ')} found.\n\n"

            self.nearest_services_label.setText(nearest_services_text.strip())
            self.update_map(paths)
            self.emergency_message_label.setText("Emergency services notified.")

    @pyqtSlot(dict)
    def on_link_clicked(self, info_dict):
        """Handle link clicks from map markers"""
        lat = info_dict["lat"]
        lon = info_dict["lon"]
        self.coord_input.setText(f"{lat}, {lon}")
        
class DisasterResponseUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Disaster Response System')
        self.setGeometry(100, 100, 1200, 600)

        # Create stacked layout
        self.stacked_layout = QStackedLayout()

        # Initialize the disaster graph
        self.disaster_graph = DisasterGraph()
        self.disaster_graph.build_from_osm("Saddar, Karachi, Pakistan")
        self.disaster_graph.load_emergency_services()
        self.disaster_graph.load_shelters()

        # Add some sample danger zones
        self.disaster_graph.add_danger_zone(24.8700, 67.0200, 200)  # Updated coordinates
        self.disaster_graph.add_danger_zone(24.8625, 67.0030, 150)  # Updated coordinates
        self.disaster_graph.add_danger_zone(24.8750, 67.0100, 300)  # Updated coordinates

        # Add welcome page
        self.welcome_page = WelcomePage(self.stacked_layout)
        self.stacked_layout.addWidget(self.welcome_page)

        # Add selection page
        self.selection_page = SelectionPage(self.stacked_layout, self)
        self.stacked_layout.addWidget(self.selection_page)

        # Add map page for rescue teams
        self.map_page = MapPage(self.stacked_layout, self.disaster_graph)
        self.stacked_layout.addWidget(self.map_page)

        # Add map page for users
        self.user_map_page = MapPage(self.stacked_layout, self.disaster_graph)
        self.stacked_layout.addWidget(self.user_map_page)

        # Set the layout
        container = QWidget()
        container.setLayout(self.stacked_layout)
        self.setCentralWidget(container)

def main():
    app = QApplication(sys.argv)
    ui = DisasterResponseUI()
    ui.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()