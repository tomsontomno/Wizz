import json
import os
from src.essentials import get_Graph, calculate_distance_coords

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
distances_json = os.path.join(base_dir, 'data', 'distances.json')
airport_coordinates_json = os.path.join(base_dir, 'data', 'airport_coordinates.json')

G = get_Graph()


def get_city_coordinates(city_name: str) -> list:
    """
    Retrieve the coordinates of the given city from the airport_coordinates.json file.

    :param city_name: Name of the city to retrieve coordinates for.
    :return: A list containing latitude and longitude of the city.
    """
    try:
        with open(airport_coordinates_json, 'r') as f:
            city_coordinates = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"'{airport_coordinates_json}' file not found.")

    if city_name in city_coordinates:
        return city_coordinates[city_name]
    else:
        raise ValueError(f"Coordinates for city '{city_name}' not found in the file.")


def calculate_all_distances(cities: list) -> dict:
    """
    Calculate the distances between all city pairs using their coordinates.

    :param cities: A list of city names.
    :return: A dictionary with city names as keys and their distances to all other cities as values.
    """
    distances = {}

    # Loop through each city
    for city_a in cities:
        coords_a = get_city_coordinates(city_a)
        distances[city_a] = {}

        # Loop through each other city to calculate distances
        for city_b in cities:
            if city_a != city_b:
                coords_b = get_city_coordinates(city_b)
                distance = calculate_distance_coords(coords_a, coords_b)
                distances[city_a][city_b] = distance

    return distances


def save_distance_to_json(distance_dict: dict, filename: str) -> None:
    """
    Save the distance dictionary to a JSON file.

    :param distance_dict: The dictionary containing city pairs and their distances.
    :param filename: The file path to save the JSON data.
    """
    with open(filename, 'w') as file:
        json.dump(distance_dict, file, indent=4)
    print(f"Distance data saved to {filename}")


if __name__ == '__main__':
    cities = list(G.nodes)
    distance_dict = calculate_all_distances(cities)
    save_distance_to_json(distance_dict, distances_json)
