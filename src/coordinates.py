import os
import json
from geopy.distance import geodesic

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
airport_coordinates_json = os.path.join(base_dir, 'data', 'airport_coordinates.json')
city_coordinates_json = os.path.join(base_dir, 'data', 'city_coordinates.json')


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


"""
# removed for now because i want to prevent accidental deletion and generally it doesnt have much usage
def remove_city_coordinate(city_name: str) -> None:
    
    Remove the coordinates of the given city from the airport_coordinates.json file.

    :param city_name: Name of the city to remove coordinates for.
    
    try:
        with open(airport_coordinates_json, 'r') as f:
            city_coordinates = json.load(f)
    except FileNotFoundError:
        print(f"No coordinates file found. Nothing to delete.")
        return

    if city_name in city_coordinates:
        del city_coordinates[city_name]
        with open(airport_coordinates_json, 'w') as f:
            json.dump(city_coordinates, f, indent=4)
        print(f"Coordinates for '{city_name}' have been removed.")
    else:
        print(f"City '{city_name}' not found in the coordinates file.")
"""


def proximity_to_airport(city_name: str) -> float:
    """
    Calculate the distance between the city coordinates in airport_coordinates.json and city_coordinates.json.

    :param city_name: Name of the city to calculate proximity for.
    :return: The distance in kilometers.
    """
    try:
        with open(airport_coordinates_json, 'r') as f:
            airport_coordinates = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"'{airport_coordinates_json}' file not found.")

    try:
        with open(city_coordinates_json, 'r') as f:
            city_coordinates = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"'{city_coordinates_json}' file not found.")

    if city_name in airport_coordinates and city_name in city_coordinates:
        coords_airport = airport_coordinates[city_name]
        coords_city = city_coordinates[city_name]
        distance = geodesic(coords_airport, coords_city).kilometers
        return distance
    else:
        raise ValueError(f"Coordinates for city '{city_name}' not found in one or both files.")
