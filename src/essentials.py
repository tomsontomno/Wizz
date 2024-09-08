import os
from math import exp
from geopy.distance import geodesic
import json
from functools import lru_cache
from src.graph_maker import load_graph


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
graph_pkl = os.path.join(base_dir, 'data', 'graph.pkl')
city_coordinates = os.path.join(base_dir, 'data', 'city_coordinates.json')
airport_coordinates = os.path.join(base_dir, 'data', 'airport_coordinates.json')
distances_json = os.path.join(base_dir, 'data', 'distances.json')

G = load_graph(graph_pkl)


def get_Graph(graph_file=graph_pkl):
    if graph_file != graph_pkl:
        return load_graph(graph_file)
    return G


# right_shift = c, horizontal_scaling = k, full_point = f, flipped = + exp()
def custom_sigmoid(x, right_shift, horizontal_scaling, full_point: float, flipped: bool) -> float:
    if flipped:
        return (1 / (1 + exp((x - right_shift) / horizontal_scaling))) * \
               (100 / (100 / (1 + exp((full_point - right_shift) / horizontal_scaling))))
    else:
        return (1 / (1 + exp(-(x - right_shift) / horizontal_scaling))) * \
               (100 / (100 / (1 + exp(-(full_point - right_shift) / horizontal_scaling))))


def calculate_distance_coords(coords_1: list, coords_2: list) -> float:
    """
    Calculate the distance between two sets of coordinates.

    :param coords_1: The first set of coordinates (latitude, longitude).
    :param coords_2: The second set of coordinates (latitude, longitude).
    :return: The distance in kilometers, rounded to one decimal place.
    """
    return round(geodesic(coords_1, coords_2).kilometers, 1)


def calculate_distance_cities(city_a: str, city_b: str, factor_a: str = "airport", factor_b: str = "airport") -> float:
    """
    Calculate the distance between two cities.

    :param city_a: The first city name.
    :param city_b: The second city name.
    :param factor_a: If coordinates from "city_a" should come from the city or the airport.
    :param factor_b: If coordinates from "city_b" should come from the city or the airport.
    :return: The distance in kilometers, rounded to one decimal place.
    """

    # Load the coordinates from JSON files
    with open(airport_coordinates, 'r') as airport_file:
        airport_coords = json.load(airport_file)

    with open(city_coordinates, 'r') as city_file:
        city_coords = json.load(city_file)

    # Determine the coordinates for city_a
    if factor_a == "city":
        coords_1 = city_coords.get(city_a)
    else:
        coords_1 = airport_coords.get(city_a)

    # Determine the coordinates for city_b
    if factor_b == "city":
        coords_2 = city_coords.get(city_b)
    else:
        coords_2 = airport_coords.get(city_b)

    # If coordinates are not found for either city, raise an error
    if not coords_1 or not coords_2:
        raise ValueError(f"Coordinates not found for {city_a} or {city_b}.")

    # Calculate the geodesic distance
    return round(geodesic(coords_1, coords_2).kilometers, 1)


# Creates a function to load and preprocess distances (cached internally)
@lru_cache(maxsize=1)
def load_and_preprocess_distances(file_path: str):
    """
    Load the distance data from a JSON file and preprocess it into a flat dictionary for efficient lookups.
    This function is cached so the file is only loaded and processed once.

    :param file_path: Path to the distances.json file.
    :return: Preprocessed flat distance dictionary.
    """
    with open(file_path, 'r') as file:
        distances = json.load(file)

    return preprocess_distances(distances)


def preprocess_distances(distances):
    """
    Preprocesses the distances data to use tuple keys (city_a, city_b) for constant-time lookups.

    :param distances: Original nested dictionary of distances.
    :return: A flat dictionary where keys are (city_a, city_b) tuples and values are distances.
    """
    flat_distances = {}

    for city_a, city_b_distances in distances.items():
        for city_b, distance in city_b_distances.items():
            # Store the distance using both (city_a, city_b) and (city_b, city_a) keys
            flat_distances[(city_a, city_b)] = distance
            flat_distances[(city_b, city_a)] = distance

    return flat_distances


# Step 2: Use this cached distance data in the route calculation
def calculate_distance_route(route: list, file_path: str = distances_json) -> float:
    """
    Efficiently calculates the total distance for a route using preprocessed distances.

    :param route: A list of city names representing the route.
    :param file_path: Path to the distances.json file (used only once, as loading is cached).
    :return: The total distance of the route in kilometers, rounded to one decimal place.
    """
    # Load and preprocess distances (cached, so this happens only once)
    flat_distances = load_and_preprocess_distances(file_path)

    total_distance = 0.0

    # Iterate through consecutive city pairs in the route and sum distances
    for i in range(len(route) - 1):
        city_a = route[i]
        city_b = route[i + 1]

        # Efficient lookup using tuple-based keys
        distance = flat_distances.get((city_a, city_b))

        # If no distance is found, handle gracefully (e.g., return an error or skip)
        if distance is None:
            raise ValueError(f"Distance between {city_a} and {city_b} not found.")

        total_distance += distance

    return round(total_distance, 1)


def evaluate_weighting(pro_weight, con_weight, pro_result, con_result) -> (float, float):
    rated = 0
    weight = 0

    if pro_weight != 0 or con_weight != 0:
        if pro_weight != 0:
            rated += pro_weight * pro_result
            weight += pro_weight
        else:
            rated += con_weight * con_result
            weight += con_weight

    return rated, weight


if __name__ == "__main__":
    distance = calculate_distance_cities("Aberdeen", "Gdansk")
    print(f"The distance between Aberdeen and Gdansk is {distance} km.")
