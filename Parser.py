def pars(file):
    f = open(file, 'r')
    f.readline()
    non = int(f.readline().split(' ')[3])
    print(non)
    network = {}
    for i in range(non):
        network[i] = {}
        #print(network)

    for line in f:
        if 'END OF METADATA' in line:
            #(print(line))
            break

    for line in f:
        if '~' in line:
            #(print(line))
            break
    for line in f:
        data = line.split('	')
        #print(data)
        network[int(data[1]) - 1][int(data[2]) - 1] = []
        #print(int(data[1]) - 1)
        #print(int(data[2]) - 1)
        network[int(data[1]) - 1][int(data[2]) - 1].append(float(data[3]))
        network[int(data[1]) - 1][int(data[2]) - 1].append(float(data[5]))
        print(network)

    return network
