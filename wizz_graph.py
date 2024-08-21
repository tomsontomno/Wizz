import json
import os
import sys

import networkx as nx

with open('edges.json', 'r') as f:
    data = json.load(f)

G = nx.Graph()
for route in data:
    city_a = route['city_a']
    city_b = route['city_b']
    distance = route['distance_km']

    G.add_edge(city_a, city_b, weight=distance)


# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')


# Restore
def enablePrint():
    sys.stdout = sys.__stdout__


def bfs_min_flights(start_city, end_city):
    bfs_shortest_paths = nx.single_source_shortest_path_length(G, start_city)
    min_flights = -1
    for destination, num_edges in bfs_shortest_paths.items():
        if destination == end_city:
            min_flights = num_edges
    return min_flights


def find_all_paths_with_n_flights(start_city, end_city, n):
    # Finds all paths with exactly n flights from start_city to end_city
    all_paths = []
    queue = [(start_city, [start_city])]

    while queue:
        (current_node, path) = queue.pop(0)
        if len(path) - 1 > n:  # Skip paths that exceed the flight limit
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


# distance list is the km between each city but is not very relevant here because it will be calculated at a later point,
# so it's left out here even-though it's calculated to make the returning list cleaner and not so deep
def calculate_path_distance(path):
    distance = 0
    distance_list = []
    for i in range(len(path) - 1):
        distance_list.append(G[path[i]][path[i + 1]]['weight'])
        distance += distance_list[-1]
    return distance


def all_paths_a_to_b(start_city, end_city, verbose=False, tolerance=0, sort_by_distance=False):
    if not verbose:
        blockPrint()

    min_flights = bfs_min_flights(start_city, end_city)
    if min_flights == -1 or min_flights > 5:
        print(f"There is no path from {start_city} to {end_city}")
        return []
    print(f"The minimal amount of flights from {start_city} to {end_city} is {min_flights}\n")

    if tolerance + min_flights > 6:
        print("Tolerance too high, total sum of flights can't exceed 6.")
        tolerance = min(6 - min_flights, tolerance)
        print("Tolerance reduced to", tolerance)

    all_paths = []
    for i in range(min_flights, min(min_flights + tolerance + 1, 7)):
        if i == min_flights:
            print("Possible paths when using minimal flights:")
        else:
            print(f"Possible paths when using minimal + {i - min_flights} flights ({i} flights):")

        paths = find_all_paths_with_n_flights(start_city, end_city, i)
        paths_with_distances = [(path, calculate_path_distance(path)) for path in paths]

        if sort_by_distance:
            paths_with_distances.sort(key=lambda x: x[1])  # Sort by the distance part of the tuple
            for path, distance in paths_with_distances:
                print(f"{distance} km ", " -> ".join(path))

        else:
            for path, distance in paths_with_distances:
                print(" -> ".join(path), f" {distance} km")
        print()

        all_paths.extend(path for path, distance in paths_with_distances)

    if not verbose:
        enablePrint()

    return all_paths


# shortest path "kilometer"
def shortest_path_km(start_city: str):
    shortest_paths = nx.single_source_dijkstra_path_length(G, start_city, weight='weight')
    distances = []
    for destination, distance in shortest_paths.items():
        if distance != 0:
            distances.append([destination, distance])
    return distances


# shortest path "amount of flights"
def shortest_path_flights(start_city: str):
    bfs_shortest_paths = nx.single_source_shortest_path_length(G, start_city)
    edges = []
    for destination, num_edges in bfs_shortest_paths.items():
        if num_edges != 0:
            edges.append([destination, num_edges])
    return edges


def sum_all_km(start_city):
    shortest_paths = nx.single_source_dijkstra_path_length(G, start_city, weight='weight')
    return sum(distance for distance in shortest_paths.values())


def sum_all_flights(start_city):
    bfs_shortest_paths = nx.single_source_shortest_path_length(G, start_city)
    return sum(num_edges for num_edges in bfs_shortest_paths.values())


def filter_routes_length(min_km: int, max_km: int):
    print("\nRoutes between", str(min_km) + "km and", str(max_km) + "km:")
    routes = [(u, v, data['weight']) for u, v, data in G.edges(data=True) if min_km <= data['weight'] <= max_km]
    routes.sort(key=lambda x: x[2])
    for u, v, weight in routes:
        print(f"{u} - {v}: {weight} km")
    print()


def filter_routes_for_city(city: str):
    if city not in G.nodes:
        print(f"{city} is not in the graph.")
        return

    neighbors = [(neighbor, data['weight']) for neighbor, data in G[city].items()]
    neighbors.sort(key=lambda x: x[1])
    print(f"{len(neighbors)} Routes connected to {city}:")

    for neighbor, distance in neighbors:
        print(f"{city} - {neighbor}: {distance} km")
    print()


def show_airport_connectivity(sort_by="routes"):
    connectivity = []
    for city in G.nodes:
        neighbors = list(G[city])
        connectivity.append((city, len(neighbors)))

    if sort_by == "routes":
        connectivity.sort(key=lambda x: x[1], reverse=True)
    elif sort_by == "alphabet":
        connectivity.sort(key=lambda x: x[0])

    for city, num_routes in connectivity:
        print(f"{num_routes} Routes connected to {city}")


# prints a metric that is calculated by adding the number of flights and kilometers from a city to all other city, lower
# in this care would be more preferable
# todo
def all_cities_metric():
    all_cities_km = []
    all_cities_flights = []
    all_nodes = G.nodes()
    for node in all_nodes:
        all_cities_km.append([node, sum_all_km(node)])
        all_cities_flights.append([node, sum_all_flights(node)])

    all_cities_km.sort(key=lambda x: x[1])
    all_cities_flights.sort(key=lambda x: x[1])

    print()
    print("Cities sorted by total kilometers:")
    for city, km in all_cities_km:
        print(f"{city}: {km} km")
    print()
    print("\nCities sorted by total flights:")
    for city, flights in all_cities_flights:
        print(f"{city}: {flights} flights")


def nearby_airport_finder(city: str, distance: int) -> list:
    # Load the JSON data
    with open('vertex_distances_to_all.json', 'r') as file:
        data = json.load(file)

    nearby_airports = [city]
    city_found = False

    # Iterate through the data to find matching cities within the distance
    for entry in data:
        if entry['city_a'] == city:
            city_found = True
            if entry['distance_km'] <= distance:
                nearby_airports.append(entry['city_b'])
        elif entry['city_b'] == city:
            city_found = True
            if entry['distance_km'] <= distance:
                nearby_airports.append(entry['city_a'])

    # If city not found in the data, return [-1]
    if not city_found:
        return []

    return nearby_airports


if __name__ == '__main__':
    pass
