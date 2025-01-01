# Disaster-Response-System
Ai intelligent disaster response system

An AI-powered system for real-time disaster management. 
This project utilizes graph-based modeling and the A* search algorithm to optimize evacuation routes during emergencies like earthquakes and floods.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Alishals28/Intelligent_Disaster_Response
   ```
2. Install required Python libraries:
   ```bash
   pip install 
        networkx 
        pandas 
        matplotlib 
        numpy 
        folium
        PyQt6 and PyQt6-WebEngine # for GUI
        osmnx # for real-world map data
        scipy # for scientific computing
        haversine # for geographic distance calculations
        scikit-learn
   ```

## Goals

- **Graph-Based Modeling:** Represent disaster-prone areas and paths as graphs.
- **Optimal Pathfinding:** Use the A* search algorithm to calculate evacuation routes.
- **Dynamic Resource Allocation:** Allocate resources using informed decisions.
- **Interactive UI:** Provide a user-friendly interface for visualizing routes and data.

## Usage

1. Run the graph creation script:
   ```bash
   python src/graph_structure.py
   ```
2. Run the a* algo script
   ```bash
   python src/graph/a_star_pathfinding.py
   ```
3. Run the GUI file
   ```bash
   python src/graph/disaster_response_ui.py
   ```
4. Test with simulated scenarios by running:
   ```bash
   python tests/test_cases.py
   ```

## Contribution

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

#in the graph_structure.py file in line 21 and 40 where the filepath for csv files are written add your local path for the csv files(respective of the path where you have saved)
