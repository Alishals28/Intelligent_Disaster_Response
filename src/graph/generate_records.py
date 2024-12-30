import csv
import random

# Function to generate random coordinates around a central point
def generate_random_coordinates(lat, lon, num_records, lat_range=0.01, lon_range=0.01):
    return [(lat + random.uniform(-lat_range, lat_range), lon + random.uniform(-lon_range, lon_range)) for _ in range(num_records)]

# Function to randomly assign types to emergency services
def random_service_type():
    return random.choice(['hospital', 'police_station', 'fire_station'])

# Generate additional emergency services records
emergency_services = [
    {"name": f"{random_service_type().replace('_', ' ').title()} {i}", "type": random_service_type(), "latitude": lat, "longitude": lon}
    for i, (lat, lon) in enumerate(generate_random_coordinates(24.8607, 67.0011, 50), start=4)
]

# Generate additional shelters records
shelters = [
    {"name": f"Shelter {i}", "capacity": random.randint(50, 300), "latitude": lat, "longitude": lon}
    for i, (lat, lon) in enumerate(generate_random_coordinates(24.8637, 67.0041, 50), start=4)
]

# Write to emergency_services.csv
with open(r'F:\AI\Project\Disaster-Response-System\src\graph\emergency_services.csv', mode='a', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=["name", "type", "latitude", "longitude"])
    for record in emergency_services:
        writer.writerow(record)

# Write to shelters.csv
with open(r'F:\AI\Project\Disaster-Response-System\src\graph\shelters.csv', mode='a', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=["name", "capacity", "latitude", "longitude"])
    for record in shelters:
        writer.writerow(record)

print("Additional records added to emergency_services.csv and shelters.csv")