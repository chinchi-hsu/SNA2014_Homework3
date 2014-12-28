import networkx;
import sys;
import subprocess;
import random;

def requestNeighbors(team, node):
    neighbors = [];
    queryCount = 0;
    process = subprocess.Popen("python3 query.py " + str(team) + " " + str(node), shell = True, stdout = subprocess.PIPE);

    counter = 0;
    neighborCount = 0;
    while True:
        line = process.stdout.readline().decode("utf-8").strip();
        if not line:
            break;
        if counter == 0 and line == "-1":           # if achieving the maximum number of requests
            return [];

        if counter in [1, 2]:
            print(line + "\t");
            sys.stdout.flush();
            if counter == 2:
                neighborCount = int(line.strip().split()[1]);
        if counter >= 3:
            row = line.split();
            neighbor = int(row[0]);
            degree = int(row[1]);
            neighbors.append((neighbor, degree));

        counter += 1;

    return neighbors if neighborCount == len(neighbors) else [];

def getSeedSubgraph(team, nodeAttrStr, edgeAttrStr):
    subgraph = networkx.Graph();
    process = subprocess.Popen("python3 query.py " + team, shell = True, stdout = subprocess.PIPE);

    counter = 0;
    nodeCount = 0;
    while True:
        line = process.stdout.readline().decode("utf-8").strip();
        if not line:
            break;
        if counter == 2:
            row = line.split();
            subgraph.graph[nodeAttrStr] = int(row[0]);
            subgraph.graph[edgeAttrStr] = int(row[1]);
        if counter == 3:
            nodeCount = int(line);
        if counter >= 4 and counter < nodeCount + 4:
            row = line.split();
            node = int(row[0]);
            subgraph.add_node(node);
        if counter >= nodeCount + 4:
            row = line.split();
            node1 = int(row[0]);
            node2 = int(row[1]);
            subgraph.add_edge(node1, node2);

        counter += 1;

    return subgraph;

def testNodeQuery(team, graph):
    ok = True;
    counter = 1;
    for node in graph.nodes():
        neighbors = requestNeighbors(team, node);
        if len(neighbors) == 0:
            print("Node {0:d} not OK".format(node));
            ok = False;
        else:
            print(counter, len(neighbors));
        counter += 1;
    if ok:
        print("OK");
    

def runRandomExpansion(team, graph, maxQueryCount, realSampleStr):
    nextNode = random.sample(graph.nodes(), 1)[0];
    print("Start: {0:d}".format(nextNode));

    for q in range(maxQueryCount):
        neighbors = requestNeighbors(team, nextNode);   # returns a list of tuples (node, degree)
        if len(neighbors) == 0:                         # if there is no neighbors returned i.e. no permission to query
            print("The quota is full");
            sys.stdout.flush();
            break;
        nextNeighbor = random.sample(neighbors, 1)[0][0];

        nextNode = nextNeighbor;
        print("Query {0:d}, next {1:d}".format(q + 1, nextNode));
        print();
        sys.stdout.flush();
        

def saveGraph(graph, fileName):
    outFile = open(fileName, "w");

    for (node1, node2) in sorted(graph.edges()):
        outFile.write("{0:d} {1:d}\n".format(node1, node2));

    outFile.close();

def main():
    team = sys.argv[1];
    outFileName = sys.argv[2];
    random.seed();
    nodeAttrStr = "nodeAttrCount";
    edgeAttrStr = "edgeAttrCount";
    realSampleStr = "sampled";
    maxQueryCount = 1000;

    graph = getSeedSubgraph(team, nodeAttrStr, edgeAttrStr);
    print("Seed subgraph read");
    print("Number of nodes:", graph.number_of_nodes());
    print("Number of edges:", graph.number_of_edges());

    #testNodeQuery(team, graph);
    runRandomExpansion(team, graph, maxQueryCount, realSampleStr);
    print("Graph expanded");
    print("Number of nodes:", graph.number_of_nodes());
    print("Number of edges:", graph.number_of_edges());
    #saveGraph(graph, outFileName);

if __name__ == "__main__":
    main();
