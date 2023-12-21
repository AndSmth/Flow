
def graph_plot(graph, network, name):   #построение изображения графа
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

    nx.draw(G, pos, with_labels=True, edgelist=edges, edge_color=colors, width=1)
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=labels,
        font_color='black'
    )

    plt.savefig(name)   #сохранение изображения
    plt.clf()


def count_cost(network):    #подсчет суммарных затрат на графе
    cost = 0
    for i in network.keys():
        for j in network[i]:
            cost += network[i][j][0]*network[i][j][1]
    return cost


def Bellman_Ford(network, source, destination): #алгоритм Беллмана-Форда для поиска кратчайшего маршрута

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


def find_eq(network, source, destination, f):   #поиск равновесной загрузки сети

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

    length_network = {}    #Поиск начальных потенциалов
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
            print("No feasible solution!")
            return "No feasible solution!"

        # Step 2.3. Change the flow
        aug_flow = float('inf')
        for i in range(len(aug_path) - 1):
            n1 = aug_path[i]
            n2 = aug_path[i + 1]
            if n2 in network[n1].keys():
                aug_flow = min(aug_flow, network[n1][n2][0] - flow[n1][n2][0])   #пускает столко машин, сколько влезает в ребро
            else:
                aug_flow = min(aug_flow, flow[n2][n1][0])
        aug_flow = min(f - max_flow, aug_flow)           #сравнение текущего потока с оставшейся корреспонденицией
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

    #Алгоритм восстановления весов

    vertex_a = [0]

    while len(vertex_a) < len(network):
        vertex_b = {}
        for i in vertex_a:
            vertex_b[i] = []
            for j in network[i].keys():
                if flow[i][j][0] < network[i][j][0]:
                    if flow[i][j][0] > 0:
                        if j not in vertex_a:
                            vertex_b[i].append(j)
                        else:
                            pass

        vertex_c = {}
        for i in vertex_a:
            vertex_c[i] = []
            for t in (network.keys()):
                if t != i:
                    for j in network[t].keys():
                        if j == i:
                            if flow[t][j][0] < network[t][j][0]:
                                if flow[t][j][0] > 0:
                                    if t not in vertex_a:
                                        vertex_c[j].append(t)
                        else:
                            pass

        for i in vertex_a:
            for j in vertex_b[i]:
                potentials[j] = potentials[i] + network[i][j][1]

        for i in vertex_a:
            for j in vertex_c[i]:
                potentials[j] = potentials[i] - network[j][i][1]

        for i in vertex_b:
            if len(vertex_b[i]) > 0:
                vertex_a.append(vertex_b[i][0])

        for i in vertex_c:
            if len(vertex_c[i]) > 0:
                vertex_a.append(vertex_c[i][0])

        counter = 0
        for i in vertex_b.keys():
            for j in vertex_c.keys():
                counter += len(vertex_b[i]) + len(vertex_c[j])
        if counter == 0:
            break

    for i in range(nn):
        for j in flow[i].keys():
            flow[i][j].append(max(potentials[j] - potentials[i], network[i][j][1]))

    return flow


def detect(network, source, destination):   #алгоритм поиска браесовских ребер
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
    return edges


if __name__ == '__main__':

    network_1 = {
        0: {1: [10, 4], 2: [8, 1]},
        1: {3: [2, 6], 4: [7, 1]},
        2: {1: [20, 1], 3: [10, 3]},
        3: {4: [4, 2]},
        4: {},
    }    #тестовая сеть общего вида

    network_2 = {
        0: {1: [5, 1], 2: [10, 4]},
        1: {2: [10, 1], 3: [10, 4]},
        2: {3: [5, 1]},
        3: {},
    }   #тестовая сеть парадокса Браеса
    network_3 = {
        0: {1: [5, 1], 2: [10, 4]},
        1: {2: [10, 1], 3: [10, 4]},
        2: {1: [4, 2000], 3: [5, 1]},
        3: {},
    }   #тестовая сеть парадокса Браеса с двусторонним ребром

    def pars(file):     #парсер для файлов данных
        f = open(file, 'r')
        f.readline()
        non = int(f.readline().split(' ')[3])
        print(non)
        parsed_network = {}
        for i in range(non):
            parsed_network[i] = {}

        for line in f:
            if 'END OF METADATA' in line:
                break

        for line in f:
            if '~' in line:
                break
        for line in f:
            data = line.split('	')
            parsed_network[int(data[1]) - 1][int(data[2]) - 1] = []
            parsed_network[int(data[1]) - 1][int(data[2]) - 1].append(float(data[3]))
            parsed_network[int(data[1]) - 1][int(data[2]) - 1].append(float(data[5]))

        return parsed_network

    def main(network, s, d, f):    #полный процесс поиска брессовских ребер в сети, в текущем виде не способен работать с сетями с двусторонними ребрами
        test_network = network.copy()

        graph_plot(test_network, test_network, '1)Original Graph')      #создание и сохранение изображения первоначального графа

        flow = find_eq(test_network, s, d, f).copy()    #поиск равновесия
        graph_plot(flow, test_network, '2)Equilibrium')     #создание и сохранение изображения графа равновесия

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

        graph_plot(reduced_graph, test_network, '3)Graph without full or empty edges')
        print(count_cost(flow))

        suspicious_edges = detect(reduced_graph, s, d)
        cut_graph = {}
        if len(suspicious_edges) == 0:
            print('No edges were deemed suspicious')
        for i in test_network:
            cut_graph[i] = test_network[i].copy()
        for edge in suspicious_edges:
            cut_graph[edge[0]].pop(edge[1])
        flow_new = (find_eq(cut_graph, s, d, f))
        print(count_cost(flow_new))
        graph_plot(flow_new, test_network, '4)Equilibrium without suspicious edges')


    network_go = pars('SiouxFalls_net.tntp')

    #банальное исключение ребер
    s = 0
    d = 23
    f = 9000

    #network_go = network_2

    og_cost = (count_cost(find_eq(network_go, s, d, f)))
    castrated_network = {}
    for i in network_go.keys():
        for j in network_go[i]:
            for k in network_go:
                castrated_network[k] = network_go[k].copy()
            castrated_network[i].pop(j)
            if find_eq(castrated_network, s, d, f) == "No feasible solution!":
                pass
            else:
                if (count_cost(find_eq(castrated_network, s, d, f))) < og_cost:
                    print('Removing edge', i, j, 'changes total costs from', og_cost, 'to', count_cost(find_eq(castrated_network, s, d, f)))

    main(network_2, 0, 3, 7)
