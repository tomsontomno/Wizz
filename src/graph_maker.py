import json
import os
import networkx as nx
import pickle

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
graph_pkl = os.path.join(base_dir, 'data', 'graph.pkl')
edges_json = os.path.join(base_dir, 'data', 'edges.json')
airport_coordinates = os.path.join(base_dir, 'data', 'airport_coordinates.json')


def create_graph(distances_json=edges_json, graph_file=graph_pkl):
    """Create a graph from the edges JSON and save it to a file."""
    print("Creating graph from edges.json...")
    G = nx.Graph()
    with open(distances_json, 'r') as f:
        data = json.load(f)

    # Iterate over each city and its connections
    for city, connections in data.items():
        for connected_city, distance in connections.items():
            # Add edge if it doesn't exist to avoid duplicating for undirected graph
            if not G.has_edge(city, connected_city):
                G.add_edge(city, connected_city, weight=distance)

    # Save the graph to a file using pickle
    with open(graph_file, 'wb') as f:
        pickle.dump(G, f)
    print(f"Graph saved to {graph_file}")


def load_graph(graph_file=graph_pkl):
    """Load a graph from a file."""
    if os.path.exists(graph_file):
        print("Loading graph from cache...")
        with open(graph_file, 'rb') as f:
            return pickle.load(f)
    else:
        raise FileNotFoundError(f"The graph file {graph_file} does not exist. Please create the graph first.")


def main():
    create_graph()

    # Load the graph
    try:
        G = load_graph()

        # Example: Print the shortest path between two cities
        city_a = "Cologne"
        city_b = "Aqaba"

        path = nx.shortest_path(G, source=city_a, target=city_b, weight='weight')
        distance = nx.shortest_path_length(G, source=city_a, target=city_b, weight='weight')
        print(f"Shortest path from {city_a} to {city_b}: {path}")
        print(f"Total distance: {distance} km")
    except FileNotFoundError as e:
        print(e)


if __name__ == "__main__":
    create_graph()
    G = load_graph()
    print(G.degree("Salerno"))
