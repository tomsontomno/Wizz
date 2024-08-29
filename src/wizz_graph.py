"""
This module provides functions to analyze flight paths between cities using graph theory. It reads data from JSON files,
builds a graph of cities and routes, and offers various functions to find paths, calculate distances, and filter routes
based on specific criteria.
"""

import json
import os
import sys
import networkx as nx

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
vertex_distances_to_all_json = os.path.join(base_dir, 'data', 'vertex_distances_to_all.json')
edges_json = os.path.join(base_dir, 'data', 'edges.json')


# Load the graph data from a JSON file and initialize the graph
with open(edges_json, 'r') as f:
    data = json.load(f)

G = nx.Graph()
for route in data:
    city_a = route['city_a']
    city_b = route['city_b']
    distance = route['distance_km']
    G.add_edge(city_a, city_b, weight=distance)


def blockPrint():
    """
    Disables printing to the console by redirecting stdout to devnull.
    """
    sys.stdout = open(os.devnull, 'w')


def enablePrint():
    """
    Restores printing to the console by resetting stdout.
    """
    sys.stdout = sys.__stdout__


def bfs_min_flights(start_city, end_city):
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


def find_all_paths_with_n_flights(start_city, end_city, n):
    """
    Finds all possible paths between two cities that have exactly n flights.

    Args:
        start_city (str): The city where the journey starts.
        end_city (str): The destination city.
        n (int): The exact number of flights for each path.

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
            if len(new_path) - 1 == n and neighbor == end_city:
                all_paths.append(new_path)
            elif len(new_path) - 1 < n:
                queue.append((neighbor, new_path))

    return all_paths


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


def all_paths_a_to_b(start_city, end_city, verbose=False, tolerance=0, sort_by_distance=False):
    """
    Finds all possible paths between two cities within a given tolerance for the number of flights.

    Args:
        start_city (str): The city where the journey starts.
        end_city (str): The destination city.
        verbose (bool, optional): If True, print details of the process. Defaults to False.
        tolerance (int, optional): The tolerance for the number of extra flights allowed. Defaults to 0.
        sort_by_distance (bool, optional): If True, sort paths by distance. Defaults to False.

    Returns:
        list: A list of paths from start_city to end_city.
    """
    if not verbose:
        blockPrint()

    min_flights = bfs_min_flights(start_city, end_city)
    if min_flights == -1 or min_flights > 5:
        print(f"There is no path from {start_city} to {end_city}")
        return []

    if tolerance + min_flights > 6:
        tolerance = min(6 - min_flights, tolerance)

    all_paths = []
    for i in range(min_flights, min(min_flights + tolerance + 1, 7)):
        paths = find_all_paths_with_n_flights(start_city, end_city, i)
        paths_with_distances = [(path, calculate_path_distance(path)) for path in paths]

        if sort_by_distance:
            paths_with_distances.sort(key=lambda x: x[1])
            for path, distance in paths_with_distances:
                print(f"{distance} km ", " -> ".join(path))
        else:
            for path, distance in paths_with_distances:
                print(" -> ".join(path), f" {distance} km")
        all_paths.extend(path for path, distance in paths_with_distances)

    if not verbose:
        enablePrint()

    return all_paths


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


def nearby_airport_finder(city, distance):
    """
    Finds all airports within a specified distance from a given city.\n
    Does not check if city exists in dataset.

    Args:
        city (str): The city to find nearby airports for.
        distance (float): The maximum distance in kilometers to consider.

    Returns:
        list: A list of nearby airports within the specified distance. If the city is not found, returns an empty list.
    """
    with open(vertex_distances_to_all_json, 'r') as file:
        data = json.load(file)
    nearby_airports = [city]

    for entry in data:
        if entry['city_a'] == city and entry['distance_km'] <= distance:
            nearby_airports.append(entry['city_b'])
        elif entry['city_b'] == city and entry['distance_km'] <= distance:
            nearby_airports.append(entry['city_a'])

    return nearby_airports


if __name__ == '__main__':
    print(nearby_airport_finder("London", 0))
