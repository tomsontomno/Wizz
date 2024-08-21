import plotly.graph_objects as go
import json
import networkx as nx
import numpy as np

with open('edges.json', 'r') as f:
    data = json.load(f)

G = nx.Graph()
for route in data:
    city_a = route['city_a']
    city_b = route['city_b']
    distance = route['distance_km']
    G.add_edge(city_a, city_b, weight=distance)

purple_nodes = sorted([node for node in G.nodes() if G.degree(node) > 30])
red_nodes = sorted([node for node in G.nodes() if 12 < G.degree(node) <= 30])
blue_nodes = sorted([node for node in G.nodes() if 5 < G.degree(node) <= 12])
black_nodes = sorted([node for node in G.nodes() if G.degree(node) <= 5])

n = len(G.nodes)
pos = {}
nodes = []

# evenly spaced angles
angles = np.linspace(0, 2 * np.pi, n, endpoint=False)


def get_divisor(nodes_group):
    if len(angles) // len(nodes_group) - 1 != 0:
        return len(angles) // len(nodes_group) - 1
    else:
        return 1


groups = [15, 7, 4, 1]
line = []
i = 0
while len(angles) != 0:
    if not black_nodes:
        groups[2] = 1
    if not blue_nodes:
        groups[1] = 1
    if not red_nodes:
        groups[0] = 1
    temp = i
    angle = angles[0]
    angles = angles[1:]
    flag = False
    if line:
        nodes.append((line.pop(0), angle))
        angle = angles[0]
        angles = angles[1:]
        i += 1
    if i % groups[0] == 0 and purple_nodes:
        if not line:
            nodes.append((purple_nodes.pop(0), angle))
            angle = angles[0]
            angles = angles[1:]
            if black_nodes:
                nodes.append((black_nodes.pop(0), angle))
            i += 2
            flag = True
        else:
            line.append(red_nodes.pop(0))
    if i % groups[1] == 0 and red_nodes:
        if flag or line:
            line.append(red_nodes.pop(0))
        else:
            nodes.append((red_nodes.pop(0), angle))
            i += 1
            flag = True
    if i % groups[2] == 0 and blue_nodes:
        if flag or line:
            line.append(blue_nodes.pop(0))
        else:
            nodes.append((blue_nodes.pop(0), angle))
            i += 1
            flag = True
    if i % groups[3] == 0 and black_nodes:
        if not flag and not line:
            nodes.append((black_nodes.pop(0), angle))
            i += 1
    if i == temp:
        i += 1

radius = 10
z_value = 0

for node, angle in nodes:
    x = radius * np.cos(angle)
    y = radius * np.sin(angle)
    pos[node] = (x, y, z_value)

x_nodes = [pos[node][0] for node in G.nodes()]
y_nodes = [pos[node][1] for node in G.nodes()]
z_nodes = [pos[node][2] for node in G.nodes()]  # ensures its a 2D structure in a 3D plane

node_colors = []
node_sizes = []
text_sizes = []

for node in G.nodes():
    degree = G.degree(node)
    if degree > 30:
        node_colors.append('purple')
        node_sizes.append(20)
        text_sizes.append(18)
    elif degree > 12:
        node_colors.append('red')
        node_sizes.append(12)
        text_sizes.append(12)
    elif degree > 5:
        node_colors.append('blue')
        node_sizes.append(10)
        text_sizes.append(10)
    else:
        node_colors.append('black')
        node_sizes.append(8)
        text_sizes.append(8)

edge_trace = []
for edge in G.edges():
    x0, y0, z0 = pos[edge[0]]
    x1, y1, z1 = pos[edge[1]]
    edge_trace.append(go.Scatter3d(
        x=[x0, x1, None], y=[y0, y1, None], z=[z0, z1, None],
        mode='lines',
        line=dict(color='black', width=0.5),
        hoverinfo='text',
        text=f'Edge: {edge[0]} - {edge[1]}',
        name=f'{edge[0]}-{edge[1]}'
    ))

node_trace = go.Scatter3d(
    x=x_nodes, y=y_nodes, z=z_nodes,
    mode='markers+text',
    marker=dict(size=node_sizes, color=node_colors),
    text=list(G.nodes()),
    textfont=dict(size=text_sizes),
    hoverinfo='text'
)

fig = go.Figure(data=edge_trace + [node_trace])

fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
    ),
    hovermode='closest',
    margin=dict(l=0, r=0, b=0, t=0),
    width=None,
    height=None,
    autosize=True,
)

fig.show()
"""
fig.write_html("wizz_routes.html", include_plotlyjs='cdn',
               full_html=False, default_height='100%', default_width='100%',
               include_mathjax='cdn')
"""