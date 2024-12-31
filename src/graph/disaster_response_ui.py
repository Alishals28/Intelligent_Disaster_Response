import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QStackedLayout, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
import folium
import io
from graph_structure import DisasterGraph  # Import the DisasterGraph class

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
    def __init__(self, disaster_graph, parent=None):
        super().__init__(parent)
        self.disaster_graph = disaster_graph
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Create a QWebEngineView to display the map
        self.map_view = QWebEngineView()
        layout.addWidget(self.map_view)

        self.setLayout(layout)
        self.update_map()

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

class DisasterResponseUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Disaster Response System')
        self.setGeometry(100, 100, 800, 600)

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

def main():
    app = QApplication(sys.argv)
    ui = DisasterResponseUI()
    ui.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()