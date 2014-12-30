import networkx;
import sys;

def readGraph(filePath):
	graph = networkx.Graph();

	for line in open(filePath, "r"):
		row = line.strip().split();
		node1 = int(row[0]);
		node2 = int(row[1]);
		graph.add_edge(node1, node2);

	return graph;

def readAttributes(graph, filePath):
	attributeCount = 0;

	for line in open(filePath, "r"):
		row = line.strip().split();
		attributeCount = len(row) - 1;

		node = None;
		for (i, item) in enumerate(row):
			if i == 0:
				node = int(row[0]);
			else:
				graph.node[node][i - 1] = int(row[i]);

	return attributeCount;

def normalize(distribution):
	sumCount = sum(distribution.values());
	if sumCount == 0:
		return False;

	for (value, count) in distribution.items():
		distribution[value] = float(count) / sumCount;

	return True;

def computeDegreeDistribution(graph, bins):
	distribution = dict();

	for node in graph.nodes():
		degree = graph.degree(node);
		if degree not in distribution:
			distribution[degree] = 0;
		distribution[degree] += 1;

	lowerBounds = sorted([item[0] for item in bins], reverse = True);
	combinedDistribution = dict();
	
	for (degree, count) in distribution.items():
		for lowerBound in lowerBounds:
			if degree >= lowerBound:
				if lowerBound not in combinedDistribution:
					combinedDistribution[lowerBound] = 0;
				combinedDistribution[lowerBound] += count;
				break;

	normalize(combinedDistribution);
	return combinedDistribution;

def computeAttributeDistribution(graph, index):
	distribution = dict();

	for node in graph.nodes():
		value = graph.node[node][index];
		if value not in distribution:
			distribution[value] = 0;
		distribution[value] += 1;

	normalize(distribution);
	return distribution;

def writeDistribution(distribution, filePath):
	with open(filePath, "w") as outFile:
		for (value, probability) in sorted(distribution.items()):
			outFile.write("{0:d} {1:f}\n".format(value, probability));

def main():
	graphFilePath = sys.argv[1];
	attributeFilePath = sys.argv[2];

	graph = readGraph(graphFilePath);
	attributeCount = readAttributes(graph, attributeFilePath);
	
	bins = [
			(1, 1),
			(2, 2),
			(3, 3),
			(4, 6),
			(7, 10),
			(11, 15),
			(16, 21),
			(22, 28),
			(29, 36),
			(37, 45),
			(46, 55),
			(56, 70),
			(71, 100),
			(101, 200),
			(201, 0)
	];
	degreeDistribution = computeDegreeDistribution(graph, bins);
	writeDistribution(degreeDistribution, "degree.txt");
	for a in range(attributeCount):
		attributeDistribution = computeAttributeDistribution(graph, a);
		writeDistribution(attributeDistribution, "node_attr_{0:d}.txt".format(a + 1));

if __name__ == "__main__":
	main();
