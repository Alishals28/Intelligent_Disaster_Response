import random
import math

def generate_random_coordinates(center_lat, center_lon, num_points, radius=1000):
    """
    Generate random coordinates around a central point within a specified radius.

    Parameters:
    center_lat (float): Latitude of the central point.
    center_lon (float): Longitude of the central point.
    num_points (int): Number of random points to generate.
    radius (int): Radius in meters within which to generate points.

    Returns:
    list: List of tuples containing the generated latitude and longitude.
    """
    random_coordinates = []
    for _ in range(num_points):
        # Convert radius from meters to degrees
        radius_in_degrees = radius / 111320

        # Generate random distance and angle
        distance = random.uniform(0, radius_in_degrees)
        angle = random.uniform(0, 2 * math.pi)

        # Calculate new coordinates
        delta_lat = distance * math.cos(angle)
        delta_lon = distance * math.sin(angle) / math.cos(math.radians(center_lat))

        new_lat = center_lat + delta_lat
        new_lon = center_lon + delta_lon

        random_coordinates.append((new_lat, new_lon))

    return random_coordinates