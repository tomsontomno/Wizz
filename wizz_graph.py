import networkx as nx
import json

with open('edges.json', 'r') as f:
    data = json.load(f)

G = nx.Graph()
for route in data:
    city_a = route['city_a']
    city_b = route['city_b']
    distance = route['distance_km']

    G.add_edge(city_a, city_b, weight=distance)


# shortest path "kilometer"
def shortest_path_km(start_city: str):
    shortest_paths = nx.single_source_dijkstra_path_length(G, start_city, weight='weight')
    print(f"Shortest paths from {start_city}:")
    for destination, distance in shortest_paths.items():
        print(f"Distance to {destination}: {distance} km")


# shortest path "amount of flights"
def shortest_path_flights(start_city: str):
    bfs_shortest_paths = nx.single_source_shortest_path_length(G, start_city)
    print(f"Shortest paths (in number of edges) from {start_city}:")
    for destination, num_edges in bfs_shortest_paths.items():
        print(f"To {destination}: {num_edges}flights")


def sum_all_km(start_city):
    shortest_paths = nx.single_source_dijkstra_path_length(G, start_city, weight='weight')
    return sum(distance for distance in shortest_paths.values())


def sum_all_flights(start_city):
    bfs_shortest_paths = nx.single_source_shortest_path_length(G, start_city)
    return sum(num_edges for num_edges in bfs_shortest_paths.values())


print("\nEdges with a weight greater than 4000:")
for u, v, data in G.edges(data=True):
    if data['weight'] > 4000:
        print(f"{u} - {v}")


all_cities_km = []
all_cities_flights = []
all_nodes = G.nodes()
for node in all_nodes:
    all_cities_km.append([node, sum_all_km(node)])
    all_cities_flights.append([node, sum_all_flights(node)])


all_cities_km.sort(key=lambda x: x[1])
all_cities_flights.sort(key=lambda x: x[1])

print("Cities sorted by total kilometers:")
for city, km in all_cities_km:
    print(f"{city}: {km} km")

print("\nCities sorted by total flights:")
for city, flights in all_cities_flights:
    print(f"{city}: {flights} flights")
