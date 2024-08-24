import json
from wizz_graph import all_paths_a_to_b, nearby_airport_finder, calculate_path_distance
import destination
from math import exp


def get_city_object(city: str) -> destination:
    """
    Retrieves a Destination object for the given city.

    Args:
        city (str): The name of the city.

    Returns:
        destination.Destination: A Destination object representing the city.
    """
    return destination.Destination(city)


def get_all_routes(city_start: str, radius_start: float, city_end: str, radius_end: float, tolerance: int):
    """
    Finds all possible routes between two cities within specified radii and tolerance.

    Args:
        city_start (str): Name of the starting city.
        radius_start (int): Radius around the starting city to search for airports.
        city_end (str): Name of the destination city.
        radius_end (int): Radius around the destination city to search for airports.
        tolerance (int): Tolerance level for the routes.

    Returns:
        list: A list of all possible routes from the start to the end city.
    """
    starts = nearby_airport_finder(city_start, radius_start)
    ends = nearby_airport_finder(city_end, radius_end)

    all_routes = []
    for start in starts:
        for end in ends:
            all_routes.extend(all_paths_a_to_b(start, end, False, tolerance, False))

    return all_routes


def get_city_set(routes):
    """
    Extracts a unique set of cities from the given routes.

    Args:
        routes (list): A list of routes, where each route is a list of city names.

    Returns:
        list: A list of unique cities that appear in the routes.
    """
    cities = set()
    for route in routes:
        for city in route:
            cities.add(city)

    return list(cities)


def show_city_info(city):
    """
    Prints detailed information about a city.

    Args:
        city (str): The name of the city.
    """
    city = get_city_object(city)

    print("City Name: " + city.get_city())
    print("Visited: " + str(city.get_city_visited()))
    print("Preferability: " + str(city.get_city_preferability()))
    print("Would Like to Visit Again: " + str(city.get_city_would_visit_again()))
    print("Reachability by Foot: " + str(city.get_reachability_by_foot()))
    print("Reachability by Public Transport: " + str(city.get_reachability_by_public_transport()))
    print("Cost of Reachability: " + str(city.get_cost_of_reachability()))
    print("Country: " + city.get_country_name_german())
    print("Local name: " + city.get_country_name_local())
    print("Country Visited: " + str(city.get_country_visited()))
    print("Country Preferability: " + str(city.get_country_preferability()))
    print("EU Member: " + str(city.get_country_eu_member()))
    print("Visa Needed: " + str(city.get_country_visa_needed()))

    # Print continent information
    print("Continent: " + city.get_continent())
    print("Rating: " + str(rating_city(city.city)) + "\n")


def get_true_weight(category: str, weight_name: str, inverse=False):
    """
    Retrieves the true weight of a route-related criterion from the weights JSON file.

    Args:
        category (str): The name of the category for which the weights are being retrieved.
        weight_name (str): The name of the weight to retrieve.
        inverse (bool, optional): If True, returns the inverse of the weight. Defaults to False.

    Returns:
        float: The calculated weight for the criterion.
    """
    with open('weights.json', 'r') as file:
        weights_data = json.load(file)
        weights_Prio = weights_data[category + "_Weights"]
        weights_Share = weights_data[category + "_Weight_Share"]

    if not inverse:
        return (weights_Prio["Prioritize_" + weight_name]) * weights_Share["Share_" + weight_name]
    else:
        # For inverse calculations (currently not needed, but added for potential future usage)
        return (1 - weights_Prio["Prioritize_" + weight_name]) * weights_Share["Share_" + weight_name]


def get_hard_criteria_city(weight_name: str):
    """
    Checks whether a city-related criterion has a hard constraint (X or -X).

    Args:
        weight_name (str): The name of the weight to check.

    Returns:
        bool or int: True if the criterion is a hard constraint, False if it's excluded, 0 otherwise.
    """
    with open('weights.json', 'r') as file:
        weights = json.load(file)["City_Weight_Share"]
    if " X" in str(weights["Share_" + weight_name]):
        return True
    elif "-X" in str(weights["Share_" + weight_name]):
        return False
    else:
        return 0


def rating_city(city: str):
    """
    Calculates the rating of a city based on various criteria.

    Args:
        city (str): The name of the city to rate.

    Returns:
        float: The calculated rating of the city.
    """
    city_obj = get_city_object(city)
    with open('weights.json', 'r') as file:
        weights_data = json.load(file)
        weights = weights_data["City_Weights"]
        weights_Share = weights_data["City_Weight_Share"]

    rating = 0
    total_weight_sum = 0

    if isinstance(get_hard_criteria_city("Unvisited_City"), bool):
        if city_obj.get_city_visited() and get_hard_criteria_city("Unvisited_City"):
            return float("-inf")
        if not city_obj.get_city_visited() and not get_hard_criteria_city("Unvisited_City"):
            return float("-inf")
    else:
        if not city_obj.get_city_visited():
            rating += get_true_weight("City", "Unvisited_City")
        else:
            rating += (1 - weights["Prioritize_Unvisited_City"]) * weights_Share["Share_Unvisited_City"]
        total_weight_sum += max(get_true_weight("City", "Unvisited_City"), get_true_weight("City", "Unvisited_City", True))

    if isinstance(get_hard_criteria_city("Unvisited_Country"), bool):
        if city_obj.get_country_visited() and get_hard_criteria_city("Unvisited_Country"):
            return float("-inf")
        if not city_obj.get_country_visited() and not get_hard_criteria_city("Unvisited_Country"):
            return float("-inf")
    else:
        if not city_obj.get_country_visited():
            rating += get_true_weight("City", "Unvisited_Country")
        else:
            rating += (1 - weights["Prioritize_Unvisited_Country"]) * weights_Share["Share_Unvisited_Country"]
        total_weight_sum += max(get_true_weight("City", "Unvisited_Country"),
                                get_true_weight("City", "Unvisited_Country", True))

    if isinstance(get_hard_criteria_city("EU_Countries"), bool):
        if city_obj.get_country_eu_member() and not get_hard_criteria_city("EU_Countries"):
            return float("-inf")
        elif not city_obj.get_country_eu_member() and get_hard_criteria_city("EU_Countries"):
            return float("-inf")
    else:
        rating += get_true_weight("City", "EU_Countries") * (1 if city_obj.get_country_eu_member() else 0)
        total_weight_sum += get_true_weight("City", "EU_Countries")

    if isinstance(get_hard_criteria_city("No_Visa_Requirement"), bool):
        if city_obj.get_country_visa_needed() and get_hard_criteria_city("No_Visa_Requirement"):
            return float("-inf")
        elif not city_obj.get_country_visa_needed() and not get_hard_criteria_city("no_Visa_Requirement"):
            return float("-inf")
    else:
        rating += get_true_weight("City", "No_Visa_Requirement") * (1 if not city_obj.get_country_visa_needed() else 0)
        total_weight_sum += get_true_weight("City", "No_Visa_Requirement")

    if city_obj.get_city_visited():
        rating += get_true_weight("City", "Revisitable_City") * (1 if city_obj.get_city_would_visit_again() else 0)
        total_weight_sum += get_true_weight("City", "Revisitable_City")

    city_pref = city_obj.get_city_preferability()
    if city_pref != -1:
        rating += get_true_weight("City", "Highly_Rated_City") * city_pref / 10
        total_weight_sum += get_true_weight("City", "Highly_Rated_City")

    rating += get_true_weight("City", "Accessibility_by_Foot") * city_obj.get_reachability_by_foot() / 10
    total_weight_sum += get_true_weight("City", "Accessibility_by_Foot")

    rating += get_true_weight("City", 
        "Accessibility_by_PublicTransport") * city_obj.get_reachability_by_public_transport() / 10
    total_weight_sum += get_true_weight("City", "Accessibility_by_PublicTransport")

    rating += get_true_weight("City", "Low_Transport_Cost_from_Airport_to_City") * city_obj.get_cost_of_reachability() / 10
    total_weight_sum += get_true_weight("City", "Low_Transport_Cost_from_Airport_to_City")

    rating += get_true_weight("City", "Overall_Accessibility") * max(city_obj.get_reachability_by_foot(), (
            3 * city_obj.get_reachability_by_public_transport() + city_obj.get_cost_of_reachability()) / 4) / 10
    total_weight_sum += get_true_weight("City", "Overall_Accessibility")

    country_pref = city_obj.get_country_preferability()
    if country_pref != -1:
        rating += get_true_weight("City", "Highly_Rated_Country") * country_pref / 10
        total_weight_sum += get_true_weight("City", "Highly_Rated_Country")

    if total_weight_sum == 0:
        return 0
    else:
        rating = (rating / total_weight_sum) * 100
        return round(rating)


def get_hard_criteria_flight(weight_name: str):
    """
    Checks whether a flight-related criterion has a hard constraint (X or -X).

    Args:
        weight_name (str): The name of the weight to check.

    Returns:
        bool or int: True if the criterion is a hard constraint, False if it's excluded, 0 otherwise.
    """
    # currently not needed but for future implementation
    with open('weights.json', 'r') as file:
        weights = json.load(file)["Flight_Weight_Share"]
    if " X" in str(weights["Share_" + weight_name]):
        return True
    elif "-X" in str(weights["Share_" + weight_name]):
        return False
    else:
        return 0


def calculate_distance(city_a: str, city_b: str) -> float:
    """
    Retrieves the distance between two cities from the vertex_distances_to_all.json data.

    Args:
        city_a (str): The name of the first city.
        city_b (str): The name of the second city.

    Returns:
        float: The distance in kilometers between the two cities, or -1 if no distance is found.
    """
    if city_a == city_b:
        return 0

    with open('vertex_distances_to_all.json', 'r') as file:
        vertex_distances = json.load(file)

    for entry in vertex_distances:
        if (entry['city_a'] == city_a and entry['city_b'] == city_b) or (
                entry['city_a'] == city_b and entry['city_b'] == city_a):
            return entry['distance_km']
    print("Distance from " + city_a + " to " + city_b + " not found.")
    return 10000.0


# right_shift = c, horizontal_scaling = k, full_point = f, flipped = + exp()
def custom_sigmoid(x, right_shift, horizontal_scaling, full_point: float, flipped: bool) -> float:
    if flipped:
        return (1 / (1 + exp((x - right_shift) / horizontal_scaling))) * \
               (100 / (100 / (1 + exp((full_point - right_shift) / horizontal_scaling))))
    else:
        return (1 / (1 + exp(-(x - right_shift) / horizontal_scaling))) * \
               (100 / (100 / (1 + exp(-(full_point - right_shift) / horizontal_scaling))))


def rating_flight(city_a: str, city_b: str):
    """
    Calculates the rating of a direct flight between two cities based on various criteria.

    Args:
        city_a (str): The departure city.
        city_b (str): The arrival city.

    Returns:
        int: The calculated rating of the flight.
    """
    rating = 0
    total_weight_sum = 0

    with open('weights.json', 'r') as file:
        weights_data = json.load(file)
        weights_Prio = weights_data["Flight_Weights"]
        weights_Share = weights_data["Flight_Weight_Share"]
    weight_short = get_true_weight("Flight", "Lower_Distance")
    weight_long = (1 - weights_Prio["Prioritize_Lower_Distance"]) * weights_Share["Share_Lower_Distance"]

    distance = calculate_distance(city_a, city_b)

    if distance != -1:
        sigmoid_short = custom_sigmoid(distance, 840, 700, 180, True)
        sigmoid_long = 1 - sigmoid_short

        if weight_short * sigmoid_short > weight_long * sigmoid_long:
            # short flight preferred
            rating += weight_short * sigmoid_short
            total_weight_sum += weight_short
        else:
            # long flight preferred
            rating += weight_long * sigmoid_long
            total_weight_sum += weight_long
    else:
        print(f"Distance between {city_a} and {city_b} not found.")

    city_a = get_city_object(city_a)
    city_b = get_city_object(city_b)
    if city_a.get_country_eu_member() or city_b.get_country_eu_member():
        rating += get_true_weight("Flight", "at_Least_one_EU_Country")
    total_weight_sum += get_true_weight("Flight", "at_Least_one_EU_Country")

    """
    # Future potential Consideration: Airport Rating
    airport_rating = get_airport_rating(city_b)  # Assuming you have a function to get the airport rating
    rating += get_true_weight("Flight", "Airport_Rating") * airport_rating / 10
    total_weight_sum += get_true_weight("Flight", "Airport_Rating")
    """

    if total_weight_sum == 0:
        return 0
    else:
        rating = (rating / total_weight_sum) * 100
        return round(rating)


def get_hard_criteria_route(weight_name: str):
    """
    Checks whether a route-related criterion has a hard constraint (X or -X).

    Args:
        weight_name (str): The name of the weight to check.

    Returns:
        bool or int: True if the criterion is a hard constraint, False if it's excluded, 0 otherwise.
    """
    # currently not needed but for future implementation
    with open('weights.json', 'r') as file:
        weights = json.load(file)["Route_Weight_Share"]
    if " X" in str(weights["Share_" + weight_name]):
        return True
    elif "-X" in str(weights["Share_" + weight_name]):
        return False
    else:
        return 0


def rating_route(route: list, original_start: str = "", original_end: str = "", radius_start: float = 0,
                 radius_end: float = 0):
    """
    Calculates the rating of an entire route based on various criteria.

    Args:
        route (list): A list of cities representing the route.
        original_start (str): The originally intended starting city
        original_end (str): The originally intended arrival city
        radius_start (float): Radius around the start city to search for airports.
        radius_end (float): Radius around the destination city to search for airports.

    Returns:
        float: The calculated rating of the route.
    """
    if len(route) < 2:
        return 0
    if original_start == "":
        original_start = route[0]
    if original_end == "":
        original_end = route[-1]

    rating = 0
    total_weight_sum = 0

    flight_ratings = []
    for i in range(len(route) - 1):
        flight_rating = rating_flight(route[i], route[i + 1])
        flight_ratings.append(flight_rating)

    from numpy import mean, std
    if flight_ratings:
        average_flight_rating = custom_sigmoid(mean(flight_ratings), 61.4, 7.2, 100, False)
        stddev_flight_rating = custom_sigmoid(std(flight_ratings), 7.9, 4.2, 0, True)

        rating += get_true_weight("Route", "High_Rated_Flights") * average_flight_rating
        total_weight_sum += get_true_weight("Route", "High_Rated_Flights")

        rating += get_true_weight("Route", "Flight_Rating_Stability") * (1 - stddev_flight_rating)
        total_weight_sum += get_true_weight("Route", "Flight_Rating_Stability")
    else:
        print("ERROR! No flight ratings\n")

    direct_distance = calculate_distance(original_start, original_end)
    total_distance = sum([calculate_distance(route[i], route[i + 1]) for i in range(len(route) - 1)])

    with open('weights.json', 'r') as file:
        weights_data = json.load(file)
        weights_Prio = weights_data["Route_Weights"]
        weights_Share = weights_data["Route_Weight_Share"]

    weight_short_route = get_true_weight("Route", "Overall_Route_Distance")
    weight_long_route = (1 - weights_Prio["Prioritize_Overall_Route_Distance"]) * weights_Share[
        "Share_Overall_Route_Distance"]

    distance_ratio = direct_distance / total_distance if total_distance else 0.01
    if distance_ratio > 1:
        distance_ratio = 1
    distance_ratio = custom_sigmoid(distance_ratio * 100, 76.6, 8.4, 100, False)

    if weight_short_route * distance_ratio > weight_long_route * (1 - distance_ratio):
        rating += weight_short_route * distance_ratio
        total_weight_sum += weight_short_route
    else:
        rating += weight_long_route * (1 - distance_ratio)
        total_weight_sum += weight_long_route

    rating += get_true_weight("Route", "Overall_Route_Distance") * distance_ratio
    total_weight_sum += get_true_weight("Route", "Overall_Route_Distance")

    city_ratings = []
    for city in route:
        city_ratings.append(rating_city(city))

    # weights start- and end-city half of a layover, since they are not as relevant as a layover city
    if len(city_ratings) > 2:
        city_ratings[-1] = (city_ratings[0] + city_ratings[-1]) // 2
        city_ratings.pop(0)

    if city_ratings:
        average_city_rating = custom_sigmoid(mean(city_ratings), 61.4, 7.2, 100, False)
        stddev_city_rating = custom_sigmoid(std(city_ratings), 7.9, 4.2, 0, True)

        rating += get_true_weight("Route", "High_Rated_Cities") * average_city_rating
        total_weight_sum += get_true_weight("Route", "High_Rated_Cities")

        rating += get_true_weight("Route", "City_Rating_Stability") * stddev_city_rating
        total_weight_sum += get_true_weight("Route", "City_Rating_Stability")
    else:
        print("ERROR! No city ratings available\n")

    start_distance = calculate_distance(route[0], original_start)
    start_distance_score = custom_sigmoid(start_distance, radius_start / 1.42, radius_start / 12, 0, True)

    weight_nearby_start = get_true_weight("Route", "Nearby_Airport_Start")
    weight_far_start = get_true_weight("Route", "Nearby_Airport_Start", inverse=True)

    if weight_nearby_start * start_distance_score > weight_far_start * (1 - start_distance_score):
        rating += weight_nearby_start * start_distance_score
        total_weight_sum += weight_nearby_start
    else:
        rating += weight_far_start * (1 - start_distance_score)
        total_weight_sum += weight_far_start

    end_distance = calculate_distance(route[-1], original_end)
    end_distance_score = custom_sigmoid(end_distance, radius_end / 1.42, radius_end / 12, 0, True)

    weight_nearby_end = get_true_weight("Route", "Nearby_Airport_End")
    weight_far_end = get_true_weight("Route", "Nearby_Airport_End", inverse=True)

    if weight_nearby_end * end_distance_score > weight_far_end * (1 - end_distance_score):
        rating += weight_nearby_end * end_distance_score
        total_weight_sum += weight_nearby_end
    else:
        rating += weight_far_end * (1 - end_distance_score)
        total_weight_sum += weight_far_end

    if total_weight_sum == 0:
        return 0
    else:
        rating = rating / total_weight_sum
        return rating


def is_route_restricted(route, forbidden_cities, forbidden_routes):
    # Check if any city in the route is forbidden
    if any(city in forbidden_cities for city in route):
        return True

    # Check if any segment of the route is forbidden
    for i in range(len(route) - 1):
        segment = [route[i], route[i + 1]]
        if segment in forbidden_routes or segment[::-1] in forbidden_routes:
            return True

    return False


def rating_all_routes(original_start: str, radius_start: float, original_end: str, radius_end: float, routes: list):
    """
    Recalculates the rating of each route based on a few extra considerations and prints them together with their
    updated rating.

    Args:
        original_start (str): The originally intended starting city
        radius_start (float): Radius around the start city to search for airports.
        original_end (str): The originally intended arrival city
        radius_end (float): Radius around the destination city to search for airports.
        routes (list): A list of routes, where each route is a list of city names.
    """

    with open('restrictions.json', 'r') as file:
        restrictions = json.load(file)
    forbidden_cities = restrictions["forbidden_cities"]
    forbidden_routes = restrictions["forbidden_routes"]

    valid_routes = []
    if not routes:
        print("No routes given.")
        return
    for route in routes:
        if not is_route_restricted(route, forbidden_cities, forbidden_routes):
            valid_routes.append(route)

    if not valid_routes:
        print("No valid routes available based on the restrictions.")
        return

    min_flights = float('inf')
    max_flights = float('-inf')
    min_distance = float('inf')
    max_distance = float('-inf')

    routes_distances = []
    for route in valid_routes:
        path_distance = calculate_path_distance(route)
        routes_distances.append(path_distance)

        num_flights = len(route) - 1
        min_flights = min(min_flights, num_flights)
        max_flights = max(max_flights, num_flights)
        min_distance = min(min_distance, path_distance)
        max_distance = max(max_distance, path_distance)

    newly_rated_routes = []

    for route in valid_routes:
        route_rating = 0
        total_weight_sum = 0

        # Number of flights considerations
        num_flights = len(route) - 1
        if num_flights == min_flights:
            route_rating += get_true_weight("Routes", "Minimum_Flights")
            total_weight_sum += get_true_weight("Routes", "Minimum_Flights")
        else:
            total_weight_sum += get_true_weight("Routes", "Minimum_Flights")

        # Fewer flights (inverse logic)
        stop_rating = custom_sigmoid(num_flights - min_flights, 1.25, 0.35, 0, True)
        weight_less_flights = get_true_weight("Routes", "Less_Flights")
        weight_more_flights = get_true_weight("Routes", "Less_Flights", inverse=True)

        if weight_less_flights * stop_rating > weight_more_flights * (1 - stop_rating):
            route_rating += weight_less_flights * stop_rating
            total_weight_sum += weight_less_flights
        else:
            route_rating += weight_more_flights * (1 - stop_rating)
            total_weight_sum += weight_more_flights

        # Distance COMPARISON (inverse logic)
        path_distance = calculate_path_distance(route)

        cut_off = 0.5  # 0 Points if the path distance is twice as long as the min_distance
        if min_distance / path_distance >= cut_off:
            distance_rating = 1 - custom_sigmoid((min_distance / path_distance) * 100, 7, 5.3, cut_off * 100, True)
        else:
            distance_rating = 0

        weight_short_distance = get_true_weight("Routes", "Overall_Route_Distance_Comparison")
        weight_long_distance = get_true_weight("Routes", "Overall_Route_Distance_Comparison", inverse=True)

        if weight_short_distance * distance_rating > weight_long_distance * (1 - distance_rating):
            route_rating += weight_short_distance * distance_rating
            total_weight_sum += weight_short_distance
        else:
            route_rating += weight_long_distance * (1 - distance_rating)
            total_weight_sum += weight_long_distance

        rating = rating_route(route, original_start, original_end, radius_start, radius_end)
        route_rating += rating * get_true_weight("Routes", "Route_Rating")
        total_weight_sum += get_true_weight("Routes", "Route_Rating")

        if total_weight_sum > 0:
            route_rating = route_rating / total_weight_sum

        newly_rated_routes.append([route, route_rating])
        print(f"Route: {route} Rating: {round(route_rating * 100)}")
    newly_rated_routes = sorted(newly_rated_routes, key=lambda x: x[1], reverse=True)
    print("\n\nSorted routes ranking:\n")
    for route, rating in newly_rated_routes:
        print(f"Route: {route}, Rating: {round(rating * 100)}")


if __name__ == '__main__':
    # test output
    rating_all_routes("Köln", 120, "Abu Dhabi", 100, get_all_routes("Köln", 120, "Abu Dhabi", 100, 0))
