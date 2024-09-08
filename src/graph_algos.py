import json
import os
from collections import Counter
import networkx as nx
from src.essentials import get_Graph
import concurrent.futures

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
distances_json = os.path.join(base_dir, 'data', 'distances.json')

G = get_Graph()


def min_amount_flights(start_city, end_city):
    """
    Finds the minimum number of flights required to travel from start_city to end_city using BFS.

    Args:
        start_city (str): The city where the journey starts.
        end_city (str): The destination city.

    Returns:
        int: The minimum number of flights, or -1 if no path exists.
    """
    bfs_shortest_paths = nx.single_source_shortest_path_length(G, start_city)
    return bfs_shortest_paths.get(end_city, -1)


def find_all_paths_with_max_n_flights(start_city, end_city, n, memo=None):
    """
    Finds all possible paths between two cities that have at most n flights using dynamic programming.

    Args:
        start_city (str): The city where the journey starts.
        end_city (str): The destination city.
        n (int): The maximum number of flights for each path.
        memo (dict): A memoization dictionary to store intermediate results.

    Returns:
        list: A list of paths, where each path is a list of city names.
    """
    if memo is None:
        memo = {}
    # Memoization key: (start_city, remaining_flights)
    memo_key = (start_city, n)

    # Check if the result is already in the memo
    if memo_key in memo:
        return memo[memo_key]
    if start_city == end_city and n >= 0:
        return [[start_city]]
    if n == 0:
        return []

    all_paths = []
    for neighbor in G.neighbors(start_city):
        sub_paths = find_all_paths_with_max_n_flights(neighbor, end_city, n - 1, memo)
        for sub_path in sub_paths:
            all_paths.append([start_city] + sub_path)

    memo[memo_key] = all_paths
    return all_paths


def find_all_paths_with_max_n_flights_no_revisits(start_city, end_city, n):
    """
    Finds all possible paths between two cities that have at most n flights, then filters out paths that contain any
    city visited more than once.

    Returns:
        list: A list of valid paths with no city visited more than once.
    """
    true_paths = []
    for path in find_all_paths_with_max_n_flights(start_city, end_city, n):
        if not any(count > 1 for count in Counter(path).values()):
            true_paths.append(path)
    return true_paths


def nearby_airport_finder(city, distance):
    """
    Finds all airports within a specified distance from a given city.
    If the city is not found, returns a list with its only content being the parameter city itself.

    Args:
        city (str): The city to find nearby airports for.
        distance (float): The maximum distance in kilometers to consider.

    Returns:
        list: A list of nearby airports within the specified distance. If the city is not found, returns a list containing parameter city.
    """
    with open(distances_json, 'r') as file:
        data = json.load(file)
    nearby_airports = [city]

    if city in data:
        city_distances = data[city]
        for nearby_city, city_distance in city_distances.items():
            if city_distance <= distance:
                nearby_airports.append(nearby_city)

    return nearby_airports


def all_paths_a_to_b(start_city, end_city, tolerance=0):
    """
    Finds all possible paths between two cities within a given tolerance for the number of flights.

    Args:
        start_city (str): The city where the journey starts.
        end_city (str): The destination city.
        tolerance (int, optional): The tolerance for the number of extra flights allowed. Defaults to 0.
    Returns:
        list: A list of paths from start_city to end_city.
    """
    min_flights = min_amount_flights(start_city, end_city)
    if min_flights == -1 or min_flights > 5:
        print(f"There is no path from {start_city} to {end_city}\n")
        return []

    if tolerance > 3:
        tolerance = 3
    all_paths = find_all_paths_with_max_n_flights_no_revisits(start_city, end_city, min_flights + tolerance)
    return all_paths


def get_all_routes(city_start: str, radius_start: float, city_end: str, radius_end: float, tolerance: int):
    """
    Finds all possible routes between two cities within specified radii and tolerance using multiprocessing.

    Args:
        city_start (str): Name of the starting city.
        radius_start (float): Radius around the starting city to search for airports.
        city_end (str): Name of the destination city.
        radius_end (float): Radius around the destination city to search for airports.
        tolerance (int): Tolerance level for the routes.

    Returns:
        list: A list of all possible routes from the start to the end city.
    """
    starts = nearby_airport_finder(city_start, radius_start)
    ends = nearby_airport_finder(city_end, radius_end)

    all_routes = []

    # Prepare all (start, end) combinations
    route_combinations = [(start, end) for start in starts for end in ends]

    # Use multiprocessing at the route combination level
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Submit each start-end combination to the pool
        futures = [executor.submit(all_paths_a_to_b, start, end, tolerance) for start, end in route_combinations]

        # Collecting results from the futures
        for future in concurrent.futures.as_completed(futures):
            all_routes.extend(future.result())

    return all_routes


def calculate_path_distance(path):
    """
    Calculates the total distance of a given path.

    Args:
        path (list): A list of city names representing the path.

    Returns:
        float: The total distance of the path in kilometers.
    """
    distance = 0
    for i in range(len(path) - 1):
        distance += G[path[i]][path[i + 1]]['weight']
    return distance


def shortest_path_km(start_city):
    """
    Finds the shortest path in kilometers from start_city to all other cities.

    Args:
        start_city (str): The city where the journey starts.

    Returns:
        list: A list of [destination, distance] pairs, sorted by distance.
    """
    shortest_paths = nx.single_source_dijkstra_path_length(G, start_city, weight='weight')
    return [[destination, distance] for destination, distance in shortest_paths.items() if distance != 0]


def shortest_path_flights(start_city):
    """
    Finds the shortest path in terms of the number of flights from start_city to all other cities.

    Args:
        start_city (str): The city where the journey starts.

    Returns:
        list: A list of [destination, num_flights] pairs, sorted by the number of flights.
    """
    bfs_shortest_paths = nx.single_source_shortest_path_length(G, start_city)
    return [[destination, num_edges] for destination, num_edges in bfs_shortest_paths.items() if num_edges != 0]


def sum_all_km(start_city):
    """
    Sums the shortest distances in kilometers from start_city to all other cities.

    Args:
        start_city (str): The city where the journey starts.

    Returns:
        float: The sum of all distances in kilometers.
    """
    shortest_paths = nx.single_source_dijkstra_path_length(G, start_city, weight='weight')
    return sum(distance for distance in shortest_paths.values())


def sum_all_flights(start_city):
    """
    Sums the shortest paths in terms of the number of flights from start_city to all other cities.

    Args:
        start_city (str): The city where the journey starts.

    Returns:
        int: The sum of all flights.
    """
    bfs_shortest_paths = nx.single_source_shortest_path_length(G, start_city)
    return sum(num_edges for num_edges in bfs_shortest_paths.values())


def filter_routes_length(min_km, max_km):
    """
    Filters and prints all routes within a specified distance range.

    Args:
        min_km (int): The minimum distance in kilometers.
        max_km (int): The maximum distance in kilometers.
    """
    routes = [(u, v, data['weight']) for u, v, data in G.edges(data=True) if min_km <= data['weight'] <= max_km]
    routes.sort(key=lambda x: x[2])
    for u, v, weight in routes:
        print(f"{u} - {v}: {weight} km")


def filter_routes_for_city(city):
    """
    Filters and prints all routes connected to a specified city.

    Args:
        city (str): The city to filter routes for.
    """
    if city not in G.nodes:
        print(f"{city} is not in the graph.")
        return

    neighbors = [(neighbor, data['weight']) for neighbor, data in G[city].items()]
    neighbors.sort(key=lambda x: x[1])
    for neighbor, distance in neighbors:
        print(f"{city} - {neighbor}: {distance} km")


def show_airport_connectivity(sort_by="routes"):
    """
    Displays the connectivity of airports, either sorted by the number of routes or alphabetically.

    Args:
        sort_by (str, optional): Criteria for sorting ('routes' or 'alphabet'). Defaults to 'routes'.
    """
    connectivity = [(city, len(list(G[city]))) for city in G.nodes]
    connectivity.sort(key=lambda x: x[1] if sort_by == "routes" else x[0], reverse=(sort_by == "routes"))

    for city, num_routes in connectivity:
        print(f"{num_routes} Routes connected to {city}")


def all_cities_metric():
    """
    Displays cities sorted by total kilometers and total flights to all other cities.
    """
    all_cities_km = [[node, sum_all_km(node)] for node in G.nodes]
    all_cities_flights = [[node, sum_all_flights(node)] for node in G.nodes]

    all_cities_km.sort(key=lambda x: x[1])
    all_cities_flights.sort(key=lambda x: x[1])

    print("Cities sorted by total kilometers:")
    for city, km in all_cities_km:
        print(f"{city}: {km} km")

    print("\nCities sorted by total flights:")
    for city, flights in all_cities_flights:
        print(f"{city}: {flights} flights")


def reference(start_city, end_city, n):
    """
    Finds all possible paths between two cities that have at most n flights.

    Args:
        start_city (str): The city where the journey starts.
        end_city (str): The destination city.
        n (int): The maximum number of flights for each path.

    Returns:
        list: A list of paths, where each path is a list of city names.
    """
    all_paths = []
    queue = [(start_city, [start_city])]

    while queue:
        current_node, path = queue.pop(0)
        if len(path) - 1 > n:
            continue
        for neighbor in G.neighbors(current_node):
            if neighbor in path:
                continue
            new_path = path + [neighbor]
            if len(new_path) - 1 <= n and neighbor == end_city:
                all_paths.append(new_path)
            if len(new_path) - 1 < n:
                queue.append((neighbor, new_path))

    return all_paths


if __name__ == '__main__':
    pass
