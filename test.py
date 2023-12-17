test_network = {
        0: {1: [10, 4], 2: [8, 1]},
        1: {3: [2, 6], 4: [7, 1]},
        2: {1: [5, 2], 3: [10, 3]},
        3: {4: [4, 2]},
        4: {},
    }
s = 0
d = 4
f = 10

import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()

for i in test_network.keys():
        G.add_node(i)
        for j in test_network[i]:
                G.add_edge(i, j)

pos = nx.random_layout(G)

labels = {
        (0, 1): test_network[0][1],
        (0, 2): 'edge2',
    }

for i in test_network.keys():
    for j in test_network[i]:
        labels[(i, j)] = test_network[i][j]

nx.draw(G, pos, with_labels = True)
nx.draw_networkx_edge_labels(
    G,
    pos,
    edge_labels=labels,
    font_color='red'
)

plt.savefig("graph.png")