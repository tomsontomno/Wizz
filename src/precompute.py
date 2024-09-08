import os
import json
from src.rating_city import rate_city
from src.rating_flight import rate_flight
from src.weights import Weights
from src.essentials import get_Graph
import multiprocessing as mp
from functools import partial

G = get_Graph()

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def compute_city_rating(city, weights):
    return city, rate_city(city, weights)


def compute_route_rating(city_a, city_b, weights):
    return city_a, city_b, rate_flight(city_a, city_b, weights)


def precompute(username, template_name, output_dir=os.path.join(base_dir, 'data')):
    weights = Weights(username, template_name)
    cities = list(G.nodes)
    routes = list(G.edges)

    true_routes = []
    for each in routes:
        true_routes.append(each)
        true_routes.append((each[1], each[0]))

    city_ratings = {}
    route_ratings = {}

    # Use multiprocessing to compute city ratings in parallel
    with mp.Pool() as pool:
        compute_city_partial = partial(compute_city_rating, weights=weights)
        city_results = pool.map(compute_city_partial, cities)

    # Collect results into city_ratings
    for city, rating in city_results:
        city_ratings[city] = rating

    # Use multiprocessing to compute route ratings in parallel
    with mp.Pool() as pool:
        compute_rating_partial = partial(compute_route_rating, weights=weights)
        route_results = pool.starmap(compute_rating_partial, true_routes)

    # Collect results into route_ratings
    for city_a, city_b, rating in route_results:
        if city_a not in route_ratings:
            route_ratings[city_a] = {}
        route_ratings[city_a][city_b] = rating

    # Prepare output directory
    user_dir = os.path.join(output_dir, username, template_name)
    os.makedirs(user_dir, exist_ok=True)

    # Store the results in a JSON file
    precomputed_data = {
        "city": city_ratings,
        "routes": route_ratings
    }
    with open(os.path.join(user_dir, 'precomputed.json'), 'w', encoding='utf-8') as f:
        json.dump(precomputed_data, f, indent=4)

    print(f"Precomputed data saved to {os.path.join(user_dir, 'precomputed.json')}")


def retrieve_precomputed_data(username, template_name, output_dir=os.path.join(base_dir, 'data')):
    user_dir = os.path.join(output_dir, username, template_name)
    file_path = os.path.join(user_dir, 'precomputed.json')

    if not os.path.exists(file_path):
        print(f"No precomputed data found at {file_path}")
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


if __name__ == "__main__":
    username = "tomsontomno"
    template_name = "template_test"

    precompute(username, template_name)

    # Retrieve the precomputed data
    precomputed_data = retrieve_precomputed_data(username, template_name)
    if precomputed_data:
        # print("City Ratings:", precomputed_data['city'])
        print("Route Ratings:", precomputed_data['routes']["Dortmund"])
