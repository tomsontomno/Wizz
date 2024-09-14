import threading
import time
import concurrent.futures
from src.graph_algos import get_all_routes
from src.essentials import get_Graph, calculate_distance_route, evaluate_weighting, custom_sigmoid
from src.rating_route import rating_route
from src.weights import Weights

G = get_Graph()
task_progress = {}
response = {}


def get_results(task_id):
    with threading.Lock():
        return response[task_id]


def get_progress_rating(task_id):
    with threading.Lock():
        if task_id not in task_progress:
            return None  # for the case that "Task not found"
        return round(100 * task_progress[task_id][0] / task_progress[task_id][1], 3)


def update_task_progress(task_id, progress_increment):
    with threading.Lock():
        task_progress[task_id][0] += progress_increment


def set_task_total(task_id, total):
    with threading.Lock():
        task_progress[task_id][1] = total


def reset_task_total(task_id):
    with threading.Lock():
        task_progress[task_id] = [0, 0]


def set_finished(task_id):
    with threading.Lock():
        task_progress[task_id] = [1, 1]


def abort(task_id):
    with threading.Lock():
        if task_id in task_progress:
            task_progress[task_id][1] = -2  # Mark task as aborted


def check_aborted(task_id):
    with threading.Lock():
        if task_progress[task_id][1] == -2:
            return True
        return False


def calculate_rating(route, original_start, original_end, radius_start, radius_end, weights):
    return tuple(route), \
           rating_route(route, weights, original_start, original_end, radius_start, radius_end)


def get_valid_routes(routes, forbidden_cities, forbidden_routes):
    """
    Checks which of the given routes are restricted based on city and route restrictions.
    The function checks if any part of the given route matches the forbidden routes or cities.

    Args:
        routes (list): A list representing the routes, each represented by a list of their cities.
        forbidden_cities (list): A list of cities that are restricted.
        forbidden_routes (list): A list of routes (lists of cities) that are restricted.

    Returns:
        list: A list of all valid routes, that are not restricted.
    """
    valid_routes_city = []
    valid_routes_total = []

    allowed = True
    for route in routes:
        for city in forbidden_cities:
            if city in route:
                allowed = False
                break
        if allowed:
            valid_routes_city.append(route)
        else:
            allowed = True

    for route in valid_routes_city:
        for i in range(len(route)):
            for j in range(i + 1, len(route) + 1):
                sub_route = route[i:j]
                if sub_route in forbidden_routes:
                    allowed = False
                    break
            if not allowed:
                break
        if allowed:
            valid_routes_total.append(route)
        else:
            allowed = True

    return valid_routes_total


def rate_all_routes(routes: list, start: str, radius_start: float, end: str, radius_end: float, task_id: str,
                    weights: Weights = None):
    """
    Recalculates the rating of each route based on a few extra considerations and prints them together with their
    updated rating.

    Args:
        routes (list): A list of routes, where each route is a list of city names.
        start (str): The originally intended starting city.
        radius_start (float): Radius around the start city to search for airports.
        end (str): The originally intended arrival city.
        radius_end (float): Radius around the destination city to search for airports.
        task_id (str): The ID of the current task to track progress.
        weights (Weights): The weights object containing user preferences.
    """
    if not weights:
        weights = Weights()

    forbidden_cities = weights.get_all_city_restrictions()
    forbidden_routes = weights.get_all_route_restrictions()
    reset_task_total(task_id)
    valid_routes = get_valid_routes(routes, forbidden_cities, forbidden_routes)

    if not valid_routes:
        print("No valid routes available based on the restrictions.")
        set_finished(task_id)
        return [[[start, "IMPOSSIBLE", end], 0.0]]
    set_task_total(task_id, len(valid_routes))
    min_flights = min(len(route) - 1 for route in valid_routes)
    max_flights = max(len(route) - 1 for route in valid_routes)
    span_flights = max_flights - min_flights
    if span_flights == 0:
        span_flights = float("inf")

    all_distances = [calculate_distance_route(route) for route in valid_routes]
    min_distance = min(all_distances)
    max_distance = max(all_distances)
    span_routes = max_distance - min_distance
    if span_routes == 0:
        span_routes = float("inf")

    ratings_dict = {}

    with concurrent.futures.ProcessPoolExecutor() as executor:
        future_to_route = {
            executor.submit(calculate_rating, route, start, end, radius_start, radius_end, weights): route
            for route in valid_routes
        }

        for future in concurrent.futures.as_completed(future_to_route):
            route_tuple, rating = future.result()
            ratings_dict[route_tuple] = rating
            update_task_progress(task_id, 1)
            if check_aborted(task_id):  # Check for abort signal
                print("ABORT REQUEST RECEIVED")
                for future_x in future_to_route:
                    future_x.cancel()  # Cancel all remaining tasks
                break

    print("ALL RATED")
    rerated_routes = []
    for i, route in enumerate(valid_routes):
        route_rating = 0
        total_weight_sum = 0
        num_flights = len(route) - 1

        # hard switch
        if weights.routes_hard_switch.get("only_minimum_flights") == 1 and num_flights != min_flights:
            continue
        if weights.routes_hard_switch.get("only_minimum_flights") == 0 and num_flights == min_flights:
            continue

        if num_flights == min_flights:
            route_rating += weights.routes_weights.get("minimum_flights")
        total_weight_sum += weights.routes_weights.get("minimum_flights")

        # Adding the previously calculated route rating
        rating = ratings_dict[tuple(route)]
        a, b = evaluate_weighting(weights.routes_weights.get("high_route_rating"),
                                  weights.routes_weights.get("low_route_rating"),
                                  rating/100, (100 - rating)/100)
        route_rating += a
        total_weight_sum += b

        # Flights amount
        a, b = evaluate_weighting(weights.routes_weights.get("less_flights"),
                                  weights.routes_weights.get("more_flights"),
                                  custom_sigmoid((num_flights - min_flights) / span_flights, 0.42, 0.084, 0, True),
                                  1 - custom_sigmoid((num_flights - min_flights) / span_flights, 0.42, 0.084, 0, True))
        route_rating += a
        total_weight_sum += b

        # Adding the previously calculated route rating
        a, b = evaluate_weighting(weights.routes_weights.get("low_overall_distance"),
                                  weights.routes_weights.get("high_overall_distance"),
                                  custom_sigmoid((calculate_distance_route(route) - min_distance) / span_routes, 0.42, 0.084, 0, True),
                                  1 - custom_sigmoid((calculate_distance_route(route) - min_distance) / span_routes, 0.42, 0.084, 0, True))
        route_rating += a
        total_weight_sum += b

        rerated_routes.append([route, round(route_rating / total_weight_sum, 3)])

    return sorted(rerated_routes, key=lambda x: x[1], reverse=True)


def rate_all(start, radius_start, end, radius_end, tolerance, task_id):
    start_time = time.time()
    routes = get_all_routes(start, radius_start, end, radius_end, tolerance)
    ranked_routes = rate_all_routes(routes, start, radius_start, end, radius_end, task_id)
    end_time = time.time()

    output = f"\nTime taken to rank {len(routes)} routes: {end_time - start_time:.4f} seconds\n"
    output += f"This equates to {len(routes) / (end_time - start_time):.4f} routes ranked per second.\n\n"
    for i, route in enumerate(ranked_routes):
        output += f"#{i + 1}\nRATING: {round(route[1] * 100, 2)}\nROUTE: {' -> '.join(route[0])}\n\n"

    with threading.Lock():
        response[task_id] = output

    update_task_progress(task_id, 1000)  # Mark progress as complete


if __name__ == '__main__':
    s = "Dortmund"
    rs = 120
    e = "Lampedusa"
    re = 0

    start_timer = time.time()
    print(rate_all(s, rs, e, re, 0, "x"))
    end_timer = time.time()
    print(f"Time taken: {end_timer - start_timer:.4f} seconds\n")
