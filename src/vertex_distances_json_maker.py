import json
import os
from geopy.distance import geodesic
from geopy.geocoders import Photon
from src.name_formatter import formated_city_name
from src.edges_json_maker import save_distance_to_json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
vertex_distances_to_all_json = os.path.join(base_dir, 'data', 'vertex_distances_to_all.json')


def get_city_coordinates(city_name):
    request_name = formated_city_name(city_name)
    geolocator = Photon(user_agent="geoapiExercises")
    location = geolocator.geocode(request_name)
    if location:
        print(f"Requesting coordinates of {city_name}")
        return location.latitude, location.longitude
    else:
        print(f"Could not find coordinates for {city_name}")
        return None


def calculate_distance(coords_1, coords_2):
    return geodesic(coords_1, coords_2).kilometers


def get_all_city_coordinates(cities):
    city_coordinates = {}
    for city in cities:
        coords = get_city_coordinates(city)
        if coords:
            city_coordinates[city] = coords
    return city_coordinates


def calculate_all_distances(city_coordinates):
    cities = list(city_coordinates.keys())
    for i in range(len(cities)):
        for j in range(i + 1, len(cities)):
            city_a = cities[i]
            city_b = cities[j]
            coords_a = city_coordinates[city_a]
            coords_b = city_coordinates[city_b]
            distance = calculate_distance(coords_a, coords_b)
            save_distance_to_json(city_a, city_b, distance, vertex_distances_to_all_json)


if __name__ == '__main__':
    cities = []

    for i in range(0, 187):
        cities.append(input())

    city_coordinates = get_all_city_coordinates(cities)
    calculate_all_distances(city_coordinates)
