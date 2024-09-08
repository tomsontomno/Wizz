import os
import json
from geopy.distance import geodesic

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
edges_json = os.path.join(base_dir, 'data', 'edges.json')
routes_txt = os.path.join(base_dir, 'data', 'raw_routes_latest.txt')
airport_coordinates_json = os.path.join(base_dir, 'data', 'airport_coordinates.json')


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


def collect_city_coordinates(routes: list) -> dict:
    """
    Collect coordinates for all cities in the routes.

    :param routes: A list of routes with city pairs.
    :return: A dictionary with city names as keys and their coordinates as values.
    """
    city_coordinates = {}
    for route in routes:
        city_a, city_b = route.strip().split(' - ')
        if city_a not in city_coordinates:
            city_coordinates[city_a] = get_city_coordinates(city_a)
        if city_b not in city_coordinates:
            city_coordinates[city_b] = get_city_coordinates(city_b)
    return city_coordinates


def calculate_distance(coords_1: list, coords_2: list) -> float:
    """
    Calculate the distance between two sets of coordinates.

    :param coords_1: The first set of coordinates (latitude, longitude).
    :param coords_2: The second set of coordinates (latitude, longitude).
    :return: The distance in kilometers.
    """
    return geodesic(coords_1, coords_2).kilometers


def create_edges_json(routes: list, city_coordinates: dict) -> None:
    """
    Create the edges JSON file with distances between city pairs.

    :param routes: A list of routes with city pairs.
    :param city_coordinates: A dictionary of city coordinates.
    """
    edges = {}

    for route in routes:
        city_a, city_b = route.strip().split(' - ')
        print(f"\nCalculating distance between {city_a} and {city_b}...", end=" ")

        distance = calculate_distance(city_coordinates[city_a], city_coordinates[city_b])
        rounded_distance = round(distance, 1)
        print(rounded_distance)

        if city_a not in edges:
            edges[city_a] = {}
        if city_b not in edges:
            edges[city_b] = {}

        edges[city_a][city_b] = rounded_distance
        edges[city_b][city_a] = rounded_distance

    save_edges_to_json(edges, edges_json)
    print(f"\nCreated '{edges_json}' with calculated distances.")


def save_edges_to_json(edges: dict, file: str) -> None:
    """
    Save the edges dictionary to a JSON file.

    :param edges: The dictionary containing city pairs and their distances.
    :param file: The file path to save the JSON data.
    """
    with open(file, 'w') as f:
        json.dump(edges, f, indent=4)


def main():
    with open(routes_txt, 'r') as f:
        routes = f.readlines()

    print("\nCollecting coordinates for all cities...")
    city_coordinates = collect_city_coordinates(routes)
    print("Coordinates collected.\n")

    create_edges_json(routes, city_coordinates)


if __name__ == '__main__':
    main()
