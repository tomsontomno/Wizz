import json
from wizz_graph import all_paths_a_to_b, nearby_airport_finder
import destination


def get_city_object(city: str) -> destination:
    """
    Retrieves a Destination object for the given city.

    Args:
        city (str): The name of the city.

    Returns:
        destination.Destination: A Destination object representing the city.
    """
    return destination.Destination(city)


def get_all_routes(city_start: str, radius_start: int, city_end: str, radius_end: int, tolerance: int):
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
            all_routes.extend(all_paths_a_to_b(start, end, True, tolerance, False))

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


def get_true_weight_city(weight_name: str, inverse=False):
    """
    Retrieves the true weight of a city-related criterion from the weights JSON file.

    Args:
        weight_name (str): The name of the weight to retrieve.
        inverse (bool, optional): If True, returns the inverse of the weight. Defaults to False.

    Returns:
        float: The calculated weight for the criterion.
    """
    with open('weights.json', 'r') as file:
        weights_data = json.load(file)
        weights_Prio = weights_data["City_Weights"]
        weights_Share = weights_data["City_Weight_Share"]

    if not inverse:
        return (weights_Prio["Prioritize_" + weight_name]) * weights_Share["Share_" + weight_name]
    else:
        # to cancel influence of any weight with an inverse calculation scheme, one has to set the corresponding
        # "Share_" weight to 0, as setting the "Prioritize_" weight to 0 will lead to the inverse statement to be 1
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
            rating += get_true_weight_city("Unvisited_City")
        else:
            rating += (1 - weights["Prioritize_Unvisited_City"]) * weights_Share["Share_Unvisited_City"]
        total_weight_sum += max(get_true_weight_city("Unvisited_City"), get_true_weight_city("Unvisited_City", True))

    if isinstance(get_hard_criteria_city("Unvisited_Country"), bool):
        if city_obj.get_country_visited() and get_hard_criteria_city("Unvisited_Country"):
            return float("-inf")
        if not city_obj.get_country_visited() and not get_hard_criteria_city("Unvisited_Country"):
            return float("-inf")
    else:
        if not city_obj.get_country_visited():
            rating += get_true_weight_city("Unvisited_Country")
        else:
            rating += (1 - weights["Prioritize_Unvisited_Country"]) * weights_Share["Share_Unvisited_Country"]
        total_weight_sum += max(get_true_weight_city("Unvisited_Country"), get_true_weight_city("Unvisited_Country", True))

    if isinstance(get_hard_criteria_city("EU_Countries"), bool):
        if city_obj.get_country_eu_member() and not get_hard_criteria_city("EU_Countries"):
            return float("-inf")
        elif not city_obj.get_country_eu_member() and get_hard_criteria_city("EU_Countries"):
            return float("-inf")
    else:
        rating += get_true_weight_city("EU_Countries") * (1 if city_obj.get_country_eu_member() else 0)
        total_weight_sum += get_true_weight_city("EU_Countries")

    if isinstance(get_hard_criteria_city("No_Visa_Requirement"), bool):
        if city_obj.get_country_visa_needed() and get_hard_criteria_city("No_Visa_Requirement"):
            return float("-inf")
        elif not city_obj.get_country_visa_needed() and not get_hard_criteria_city("no_Visa_Requirement"):
            return float("-inf")
    else:
        rating += get_true_weight_city("No_Visa_Requirement") * (1 if not city_obj.get_country_visa_needed() else 0)
        total_weight_sum += get_true_weight_city("No_Visa_Requirement")

    if city_obj.get_city_visited():
        rating += get_true_weight_city("Revisitable_City") * (1 if city_obj.get_city_would_visit_again() else 0)
        total_weight_sum += get_true_weight_city("Revisitable_City")

    city_pref = city_obj.get_city_preferability()
    if city_pref != -1:
        rating += get_true_weight_city("Highly_Rated_City") * city_pref / 10
        total_weight_sum += get_true_weight_city("Highly_Rated_City")

    rating += get_true_weight_city("Accessibility_by_Foot") * city_obj.get_reachability_by_foot() / 10
    total_weight_sum += get_true_weight_city("Accessibility_by_Foot")

    rating += get_true_weight_city("Accessibility_by_PublicTransport") * city_obj.get_reachability_by_public_transport() / 10
    total_weight_sum += get_true_weight_city("Accessibility_by_PublicTransport")

    rating += get_true_weight_city("Low_Transport_Cost_from_Airport_to_City") * city_obj.get_cost_of_reachability() / 10
    total_weight_sum += get_true_weight_city("Low_Transport_Cost_from_Airport_to_City")

    rating += get_true_weight_city("Overall_Accessibility") * max(city_obj.get_reachability_by_foot(), (
            3 * city_obj.get_reachability_by_public_transport() + city_obj.get_cost_of_reachability()) / 4) / 10
    total_weight_sum += get_true_weight_city("Overall_Accessibility")

    country_pref = city_obj.get_country_preferability()
    if country_pref != -1:
        rating += get_true_weight_city("Highly_Rated_Country") * country_pref / 10
        total_weight_sum += get_true_weight_city("Highly_Rated_Country")

    if total_weight_sum == 0:
        return 0
    else:
        rating = (rating / total_weight_sum) * 100
        return round(rating)


# todo
def rating_flight():
    """Placeholder function to calculate the rating of a flight."""
    pass


# todo
def rating_route():
    """Placeholder function to calculate the rating of a route."""
    pass


# todo
def rating_all_routes(routes):
    """
    Prints the rating of each city that appears in the given routes.

    Args:
        routes (list): A list of routes, where each route is a list of city names.
    """
    import networkx as nx
    G = nx.Graph()
    for route in routes:
        while len(route) > 1:
            G.add_edge(route[0], route[1])
            route.pop(0)

    ranking = []
    for each in G.nodes:
        ranking.append([each, rating_city(each)])
    ranking_sorted = sorted(ranking, key=lambda x: x[1], reverse=True)
    for city, rating in ranking_sorted:
        print(f"{city}: {rating}")


if __name__ == '__main__':
    # test output
    rating_all_routes(get_all_routes("Köln", 120, "Abu Dhabi", 100, 1))
