import json
from geopy.distance import geodesic
from geopy.geocoders import Photon
from name_formatter import formated_city_name


def get_city_coordinates(city_name):
    request_name = formated_city_name(city_name)
    geolocator = Photon(user_agent="geoapiExercises")
    location = geolocator.geocode(request_name)
    return location.latitude, location.longitude


def calculate_distance(city_a, city_b):
    coords_1 = get_city_coordinates(city_a)
    coords_2 = get_city_coordinates(city_b)
    return geodesic(coords_1, coords_2).kilometers


def is_pair_in_json(city_a, city_b, filename):
    try:
        with open(filename, 'r') as file:
            file_content = file.read().strip()
            if file_content:
                distances = json.loads(file_content)
            else:
                distances = []
    except FileNotFoundError:
        return False

    for entry in distances:
        if (entry['city_a'] == city_a and entry['city_b'] == city_b) or \
                (entry['city_a'] == city_b and entry['city_b'] == city_a):
            return True

    return False


def save_distance_to_json(city_a, city_b, distance,):
    data = {
        "city_a": city_a,
        "city_b": city_b,
        "distance_km": round(distance / 10) * 10
    }

    try:
        with open(filename, 'r') as file:
            file_content = file.read().strip()
            if file_content:
                distances = json.loads(file_content)
            else:
                distances = []
    except FileNotFoundError:
        distances = []

    distances.append(data)
    with open(filename, 'w') as file:
        json.dump(distances, file, indent=4)
    print(f"Distance between {city_a} and {city_b} of {data['distance_km']} km was saved in '{filename}'.")


def delete_entries_by_city(city_name):
    try:
        with open(filename, 'r') as file:
            file_content = file.read().strip()
            if file_content:
                distances = json.loads(file_content)
            else:
                distances = []
    except FileNotFoundError:
        print(f"\nFile '{filename}' not found.")
        return

    original_count = len(distances)
    distances = [entry for entry in distances if entry['city_a'] != city_name and entry['city_b'] != city_name]
    removed_count = original_count - len(distances)

    with open(filename, 'w') as file:
        json.dump(distances, file, indent=4)

    print(f"\nRemoved {removed_count} entries containing the city '{city_name}' from '{filename}'.")


def update_json():
    city_pairs = []
    for i in range(0, amount_inputs):
        x = list(input().split(" - "))
        city_pairs.append([x[0], x[1]])

    for city_pair in city_pairs:
        city_a, city_b = city_pair

        if is_pair_in_json(city_a, city_b, filename):
            print(f"\nPair {city_a} - {city_b} or its reciprocal is already in the file. Skipping API call.")
            continue

        print(f"\nCalculating distance between {city_a} and {city_b}...", end=" ")
        distance = calculate_distance(city_a, city_b)
        print(distance)

        if distance is not None:
            save_distance_to_json(city_a, city_b, distance)
        else:
            print(f"\nCould not calculate distance between {city_a} and {city_b}.")


if __name__ == '__main__':
    filename = "edges.json"
    # amount_inputs = int(input("How many entries? "))
    # delete_entries_by_city()

    amount_inputs = 1546
    update_json()
