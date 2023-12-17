
# @Statement : The dual algorithm to solve the minimum-cost flow problem
# The minimum-cost flow problem aims to find the cheapest possible way of sending a certain amount of flow through a flow network.

def graph_plot(graph, network, name):
    import networkx as nx
    import matplotlib.pyplot as plt

    G = nx.DiGraph(directed=True)

    for i in graph.keys():
        G.add_node(i)
        for j in graph[i]:
            for color in "bgrcmyk":
                if graph[i][j][0] == 0:
                    G.add_edge(i, j, color='green')
                else:
                    if graph[i][j][0] == network[i][j][0]:
                        G.add_edge(i, j, color='red')
                    else:
                        G.add_edge(i, j, color='yellow')

    pos = nx.planar_layout(G)

    labels = {}

    for i in graph.keys():
        for j in graph[i]:
            labels[(i, j)] = graph[i][j]

    edges, colors = zip(*nx.get_edge_attributes(G, 'color').items())

    nx.draw(G, pos, with_labels=True, edgelist=edges, edge_color=colors, width=2)
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=labels,
        font_color='black'
    )

    #print(G)
    plt.savefig(name)
    plt.clf()
    #plt.show()


def count_cost(network):
    cost = 0
    for i in network.keys():
        for j in network[i]:
            cost += network[i][j][0]*network[i][j][1]
    return cost

def Bellman_Ford(network, source, destination):
    """
    The Bellman-Ford algorithm to solve the shortest path problem with negative weights
    :param network: {node1: {node2: weight, node3: weight, ...}, ...}
    :param source: the source node
    :param destination: the destination node
    :return:
    """
    # Step 1. Initialization
    nn = len(network)  # node number
    dis = [float('inf')] * nn  # the distance set
    path = [[]] * nn  # the path set
    dis[source] = 0
    path[source] = [source]

    # Step 2. The main loop
    for _ in range(nn - 1):
        for i in range(nn):
            if dis[i] != float('inf'):
                for j in network[i].keys():
                    if dis[i] + network[i][j] < dis[j]:
                        dis[j] = dis[i] + network[i][j]
                        temp_path = path[i].copy()
                        temp_path.append(j)
                        path[j] = temp_path

    # Step 3. Judge if the path contains a negative weight cycle
    for i in range(nn):
        if dis[i] != float('inf'):
            for j in network[i].keys():
                if dis[i] + network[i][j] < dis[j]:
                    print('The network contains negative weight cycles')
                    return [], float('inf')
    return path[destination], dis[destination]


def find_eq(network, source, destination, f):
    """
    The main function of the dual algorithm
    :param network: flow network, {node1: {node2: [capacity, cost], node3: [capacity, cost], ...}, ...}
    :param source: the source node
    :param destination: the destination node
    :param f: the pre-defined amount of flow
    :return:
    """
    # Step 1. Initialization
    nn = len(network)  # node number
    result_network = network
    max_flow = 0
    cost = 0
    flow = {}  # flow
    for i in range(nn):
        flow[i] = {}
        for j in network[i].keys():
            flow[i][j] = [0]

    # Step 2. The main loop

    # Поиск начальных потенциалов
    length_network = {}
    for i in range(nn):
        length_network[i] = {}
    for i in range(nn):
        for j in network[i].keys():
            if flow[i][j][0] < network[i][j][0]:
                length_network[i][j] = network[i][j][1]
            if flow[i][j][0] > 0:
                length_network[j][i] = -network[i][j][1]

    potentials = {}
    for i in range(nn):
        potentials[i] = (Bellman_Ford(length_network, source, i)[1])

    while max_flow < f:

        # Step 2.1. Establish the length network
        length_network = {}
        for i in range(nn):
            length_network[i] = {}
        for i in range(nn):
            for j in network[i].keys():
                if flow[i][j][0] < network[i][j][0]:
                    length_network[i][j] = network[i][j][1]
                if flow[i][j][0] > 0:
                    length_network[j][i] = -network[i][j][1]

        # Step 2.2. Find an augmenting path
        aug_path, aug_cost = Bellman_Ford(length_network, source, destination)
        if not aug_path:  # there does not exist an augmenting path
            return print("No feasible solution!")

        # Step 2.3. Change the flow
        aug_flow = float('inf')
        for i in range(len(aug_path) - 1):
            n1 = aug_path[i]
            n2 = aug_path[i + 1]
            if n2 in network[n1].keys():
                aug_flow = min(aug_flow, network[n1][n2][0] - flow[n1][n2][0])
            else:
                aug_flow = min(aug_flow, flow[n2][n1][0])
        aug_flow = min(f - max_flow, aug_flow)
        max_flow += aug_flow
        for i in range(len(aug_path) - 1):
            n1 = aug_path[i]
            n2 = aug_path[i + 1]
            if n2 in network[n1].keys():
                flow[n1][n2][0] += aug_flow
                cost += aug_flow * network[n1][n2][1]
            else:
                flow[n2][n1][0] -= aug_flow
                cost -= aug_flow * network[n2][n1][1]
    # Алгоритм восстановления весов
    vertex_a = [0]

    while len(vertex_a) < len(network):
        vertex_b = {}
        for i in vertex_a:
            vertex_b[i] = []
            for j in network[i].keys():
                if flow[i][j][0] < network[i][j][0]:
                    if j not in vertex_a:
                        vertex_b[i].append(j)
                    else:
                        pass
                        #print(vertex_b)
        #print(vertex_b)

        vertex_c = {}
        for i in vertex_a:
            vertex_c[i] = []
            for t in (network.keys()):
                if t != i:
                    for j in network[t].keys():
                        if j == i:
                            if flow[t][j][0] < network[t][j][0]:
                                if t not in vertex_a:
                                    vertex_c[j].append(t)
                        else:
                            pass
                                    #print(vertex_c)
        #print(vertex_c)

        #print(potentials)
        for i in vertex_a:
            for j in vertex_b[i]:
                potentials[j] = potentials[i] + network[i][j][1]
                #print('+', potentials)

        for i in vertex_a:
            for j in vertex_c[i]:
                potentials[j] = potentials[i] - network[j][i][1]
                #print('-', potentials)

        for i in vertex_b:
            if len(vertex_b[i]) > 0:
                vertex_a.append(vertex_b[i][0])
                #print(vertex_a)

        #print('C', vertex_c)
        for i in vertex_c:
            #print(type(vertex_c[i]))
            if len(vertex_c[i]) > 0:
                vertex_a.append(vertex_c[i][0])
                #print(vertex_a)

        #print('mn:', vertex_a, vertex_b, vertex_c)

    for i in range(nn):
        for j in flow[i].keys():
            #print(i, j, ':', potentials[j] - potentials[i])
            flow[i][j].append(max(potentials[j] - potentials[i], network[i][j][1]))

    return flow


def detect(network, source, destination):
    neg_network = {}
    for i in network.keys():
        neg_network[i] = network[i].copy()
    for i in network.keys():
        for j in network[i]:
            neg_network[i][j] = network[i][j][1]
            neg_network[j][i] = -network[i][j][1]
    path = Bellman_Ford(neg_network, source, destination)[0]
    edges = []
    for k in range(len(path))[1:len(path)]:
        j = path[k]
        i = path[k-1]
        if neg_network[i][j] < 0:
            edges.append([j, i])
        #print(path)
        #print(i,j)
    return edges


if __name__ == '__main__':

    network_1 = {
        0: {1: [10, 4], 2: [8, 1]},
        1: {3: [2, 6], 4: [7, 1]},
        2: {1: [5, 2], 3: [10, 3]},
        3: {4: [4, 2]},
        4: {},
    }

    network_2 = {
        0: {1: [5, 1], 2: [10, 4]},
        1: {2: [10, 1], 3: [10, 4]},
        2: {3: [5, 1]},
        3: {},
    }
    network_3 = {
        1: {2: [5, 1], 3: [10, 4]},
        2: {3: [10, 1], 4: [10, 4]},
        3: {4: [5, 1]},
        4: {},
    }

    #s = 0
    #d = 4
    #f = 10

    def pars(file):
        f = open(file, 'r')
        f.readline()
        non = int(f.readline().split(' ')[3])
        print(non)
        parsed_network = {}
        for i in range(non):
            parsed_network[i] = {}

        for line in f:
            if 'END OF METADATA' in line:
                # (print(line))
                break

        for line in f:
            if '~' in line:
                # (print(line))
                break
        for line in f:
            data = line.split('	')
            # print(data)
            parsed_network[int(data[1]) - 1][int(data[2]) - 1] = []
            # print(int(data[1]) - 1)
            # print(int(data[2]) - 1)
            parsed_network[int(data[1]) - 1][int(data[2]) - 1].append(float(data[3]))
            parsed_network[int(data[1]) - 1][int(data[2]) - 1].append(float(data[5]))
            #print(network)

        return parsed_network

    def main(network, s, d, f):
        test_network = network.copy()

        graph_plot(test_network, test_network, 'Original Graph')

        flow = find_eq(test_network, s, d, f).copy()

        graph_plot(flow, test_network, 'Equilibrium')

        reduced_graph = {}
        for i in test_network:
            reduced_graph[i] = test_network[i].copy()

        for i in flow.keys():
            for j in flow[i]:
                if flow[i][j][0] == 0:
                    reduced_graph[i].pop(j)
                else:
                    if flow[i][j][0] == test_network[i][j][0]:
                        reduced_graph[i].pop(j)

        graph_plot(reduced_graph, test_network, 'Graph without full or empty edges')
        #print(test_network)
        #print(flow)
        #print(reduced_graph)
        #flow = find_eq(reduced_graph, s, d, f)
        #print(flow)
        print(count_cost(flow))



        suspicious_edges = detect(reduced_graph, s, d)
        cut_graph = {}
        if len(suspicious_edges) == 0:
            print('No edges were deemed suspicious')
        for i in test_network:
            cut_graph[i] = test_network[i].copy()
        for edge in suspicious_edges:
            cut_graph[edge[0]].pop(edge[1])
        #print(cut_graph)
        flow_new = (find_eq(cut_graph, s, d, f))
        #print(reduced_graph)
        #print(detect(reduced_graph, s, d))
        print(count_cost(flow_new))
        graph_plot(flow_new, test_network, 'Equilibrium without suspicious edges')

    network_go = pars('TEST.tntp')
    #print(network_go)

    main(network_2, 0, 3, 6)