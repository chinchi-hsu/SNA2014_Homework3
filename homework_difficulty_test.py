import networkx;
import sys;
import random;
import math;

class extendedGraph(networkx.Graph):
	def __init__(self):
		super().__init__();
		self.degreeDist = dict();
		self.attributeDists = list();
		self.attributeCount = 0;
		self.closeness = dict();
		self.attributeMaxValues = list();

	def getOrderedClosnessCentralityList(self):
		return sorted(self.closeness.items(), key = lambda item: item[1], reverse = True);

	def getNodeAttributeCount(self):
		return self.attributeCount;

	def getNodeAttributeDistribution(self, attribute):
		try:
			return self.attributeDists[attribute];
		except:
			print("attribute:", attribute, ", count:", len(self.attributeDists));
			quit();

	def getDegreeDistribution(self):
		return self.degreeDist;

	def loadFromFile(self, fileName):
		self.clear();

		with open(fileName, "r") as inFile:
			for line in inFile:
				row = line.strip().split();
				node1 = int(row[0]);
				node2 = int(row[1]);
				self.add_edge(node1, node2);

	def loadNodeAttributes(self, fileName):
		for node in self.nodes():	# clear old attributes
			for a in range(self.attributeCount):
				del self.node[node][a];

		with open(fileName, "r") as inFile:
			for line in inFile:
				row = line.strip().split();
				self.attributeCount = len(row) - 1;
				if len(self.attributeMaxValues) < self.attributeCount:
					self.attributeMaxValues = [0 for a in range(self.attributeCount)];

				node = None;
				for (i, value) in enumerate(row):
					if i == 0:
						node = int(value);
					else:
						value = int(value);
						self.node[node][i - 1] = value;
						if self.attributeMaxValues[i - 1] < value:
							self.attributeMaxValues[i - 1] = value;

	def loadClosenessCentrality(self, filePath):
		self.closeness.clear();

		with open(filePath, "r") as inFile:
			for line in inFile:
				row = line.strip().split();
				node = int(row[0]);
				closeness = float(row[1]);
				self.closeness[node] = closeness;

	def saveGraph(self, filePath):
		with open(filePath, "w") as outFile:
			for (node1, node2) in sorted(self.edges()):
				outFile.write("{0:d}\t{1:d}\n".format(node1, node2));

	def setRandomSeedGraph(self, supergraph, nodeCount):
		self.clear();
		nodeSet = set(sorted(supergraph.nodes(), key = lambda node: supergraph.degree(node), reverse = True)[ : 100]);
		for node1 in nodeSet:
			for node2 in nodeSet:
				if node1 < node2 and supergraph.has_edge(node1, node2):
					self.add_edge(node1, node2);
					
		"""
		self.clear();
		
		node = random.sample(supergraph.nodes(), 1)[0];
		nodeSet = set([node]);
		self.add_node(node);
		
		while self.number_of_nodes() < nodeCount:
			#print("Seed:", len(nodeSet));
			node = random.sample(nodeSet, 1)[0];
			neighbor = random.sample(supergraph.neighbors(node), 1)[0];
			
			if neighbor in nodeSet:
				continue;

			nodeSet.add(neighbor);
			self.add_node(neighbor);
			
			neighborNeighborSet = set(supergraph.neighbors(neighbor));
			edgeSideSet = neighborNeighborSet & nodeSet;
			for endpoint in edgeSideSet:
				self.add_edge(neighbor, endpoint);
		"""

	def runMaxDegreeExpansion(self, supergraph, maxQueryCount, outFile):
		# these nodes should not be queried if their neighbors are known
		visitedNodeSet = set();

		for q in range(maxQueryCount):
			candidates = sorted(self.nodes(), key = self.degree, reverse = True);
			node = None;
			for i in range(len(candidates)):
				candidate = candidates[i];
				if candidate not in visitedNodeSet:
					if self.degree(candidate) == supergraph.degree(candidate):	# if all adjacent edges are found, it is unnecessary to query the node
						visitedNodeSet.add(candidate);
					else:
						node = candidate;
						break;
			if node == None:
				print("All known nodes are visited");
				break;
			visitedNodeSet.add(node);	# query the node

			for neighbor in supergraph.neighbors(node):
				self.add_node(neighbor);
				self.add_edge(node, neighbor);

			print("Expansion:\t", q + 1, "\t", self.number_of_nodes(), "\t", self.number_of_edges());
			outFile.write(str(q + 1) + "\t" + str(self.number_of_nodes()) + "\t" + str(self.number_of_edges()) + "\n");
			outFile.flush();

	def isSubgraph(self, supergraph):
		for node in self.nodes():
			if not supergraph.has_node(node):
				return False;

		for (node1, node2) in self.edges():
			if not supergraph.has_edge(node1, node2):
				return False;

		return True;
		
	def computeDegreeDistribution(self, binBounds):
		degreeDist = dict();
		maxDegree = 0;

		for node in self.nodes():
			degree = self.degree(node);
			if maxDegree < degree:
				maxDegree = degree;

			if degree not in degreeDist:
				degreeDist[degree] = 0;
			degreeDist[degree] += 1;

		binBounds = sorted(binBounds);
		for binLowerBound in binBounds:
			self.degreeDist[binLowerBound] = 0;
		
		for (degree, count) in degreeDist.items():	# bin combination
			for i in range(len(binBounds) - 1, -1, -1):
				binLowerBound = binBounds[i];
				if degree >= binLowerBound:
					self.degreeDist[binLowerBound] += count;
					break;

		totalCount = 0;	# +1 smoothing
		for (bin, count) in self.degreeDist.items():
			self.degreeDist[bin] = count + 1;
			totalCount += self.degreeDist[bin];

		for (degree, count) in self.degreeDist.items():	# normalization
			self.degreeDist[degree] = float(count) / totalCount;

	def computeNodeAttributeDistributions(self, supergraph = None):
		if supergraph != None:
			self.attributeCount = supergraph.getNodeAttributeCount();
		self.attributeDists = [dict() for a in range(self.attributeCount)];

		for (a, attributeDist) in enumerate(self.attributeDists):
			for node in self.nodes():
				value = self.node[node][a] if supergraph == None else supergraph.node[node][a];
				if value not in attributeDist:
					attributeDist[value] = 0;
				attributeDist[value] += 1;

			totalCount = 0;	# +1 smoothing
			maxValue = self.attributeMaxValues[a] if supergraph == None else supergraph.attributeMaxValues[a];
			for value in range(maxValue + 1):
				if value not in attributeDist:
					attributeDist[value] = 0;
				attributeDist[value] += 1;
				totalCount += attributeDist[value];

			for (value, count) in attributeDist.items():	# normalization
				attributeDist[value] = float(count) / totalCount;
	
	def evaluateKLDivergence(self, referenceDist, approximateDist):
		KLDivergence = 0.0;
		for (degree, referenceProb) in referenceDist.items():
			if degree in approximateDist:
				approximateProb = approximateDist[degree];
				KLDivergence += referenceProb * math.log(referenceProb / approximateProb);
		return KLDivergence;

	def compareDistribution(self, selfDist, anotherDist):
		KL1 = self.evaluateKLDivergence(selfDist, anotherDist);
		KL2 = self.evaluateKLDivergence(anotherDist, selfDist);
		return (KL1 + KL2) / 2;

	def writeDistribution(self, filePath, distribution):
		with open(filePath, "w") as outFile:
			for (degree, probability) in sorted(distribution.items()):
				outFile.write(str(degree) + "\t" + str(probability) + "\n");

	def writeDegreeDistribution(self, filePath):
		self.writeDistribution(filePath, self.degreeDist);

	def writeNodeAttributeDistribution(self, filePath, attribute):
		self.writeDistribution(filePath, self.attributeDists[attribute]);

	def writeClosenessCentrality(self, filePath, topK):
		closenessList = self.getOrderedClosnessCentralityList();

		with open(filePath, "w") as outFile:
			for (count, (node, score)) in enumerate(closenessList):
				if count >= topK:
					break;
				outFile.write(str(node) + "\t" + str(score) + "\n");	
	
	def compareDegreeDistribution(self, anotherGraph):
		return self.compareDistribution(self.degreeDist, anotherGraph.getDegreeDistribution());

	def compareNodeAttributeDistribution(self, anotherGraph, attribute):
		return self.compareDistribution(self.attributeDists[attribute], anotherGraph.getNodeAttributeDistribution(attribute));

	def computeClosenessCentrality(self):
		self.closeness = networkx.closeness_centrality(self);

	def evaluateClosenessCentralityRanks(self, supergraph, topK):
		supergraphClosenessList = supergraph.getOrderedClosnessCentralityList();

		meanTrueRanks = 0.0;
		for (count, (node, score)) in enumerate(sorted(self.closeness.items(), key = lambda item: item[1], reverse = True)):
			if count >= topK:
				break;

			trueRank = 0;
			for (rank, (referredNode, referredScore)) in enumerate(supergraphClosenessList):
				if referredNode == node:
					trueRank = rank + 1;
					break;
			
			meanTrueRanks += trueRank;

		return meanTrueRanks / topK;

def main():
	graphFilePath = sys.argv[1];
	attributeFilePath = sys.argv[2];
	closenessFilePath = sys.argv[3];
	postfix = sys.argv[4];

	graph = extendedGraph();
	graph.loadFromFile(graphFilePath);
	graph.loadNodeAttributes(attributeFilePath);
	print("Graph:", graph.number_of_nodes(), graph.number_of_edges());
	print("Connected:", networkx.is_connected(graph));
	print("Graph loaded");
	random.seed();

	binBounds = [1, 2, 3, 4, 7, 11, 16, 22, 29, 37, 46, 56, 71, 101, 201];
	graph.computeDegreeDistribution(binBounds);
	graph.computeNodeAttributeDistributions();
	graph.loadClosenessCentrality(closenessFilePath);

	graph.writeDegreeDistribution(postfix + "_graph_degree.txt");
	for a in range(graph.getNodeAttributeCount()):
		graph.writeNodeAttributeDistribution(postfix + "_graph_node_attribute_" + str(a + 1) + ".txt", a);

	seedNodeCounts = [i for i in range(25, 101, 25)];
	maxQueryCounts = [i for i in range(100, 1001, 100)];
	degreeDistTable = dict();
	closenessRankTable = dict();
	nodeAttributeDistTables = [dict() for a in range(graph.getNodeAttributeCount())];

	for seedNodeCount in seedNodeCounts:
		for maxQueryCount in maxQueryCounts:
			outFile = open(postfix + "_record_" + str(seedNodeCount) + "_" + str(maxQueryCount) + ".txt", "w");

			subgraph = extendedGraph();
			subgraph.setRandomSeedGraph(graph, seedNodeCount);
			subgraph.saveGraph(postfix + "_seed_" + str(seedNodeCount) + "_" + str(maxQueryCount) + ".txt");
			
			print("Seed node count:", seedNodeCount)
			print("Max query count:", maxQueryCount);
			print("Seed:", subgraph.number_of_nodes(), subgraph.number_of_edges());
			print("Seed is connected:", networkx.is_connected(subgraph));

			subgraph.runMaxDegreeExpansion(graph, maxQueryCount, outFile);

			print("Graph:", graph.number_of_nodes(), graph.number_of_edges());
			print("Subgraph:", subgraph.number_of_nodes(), subgraph.number_of_edges());
			print("is subgraph:", subgraph.isSubgraph(graph));

			subgraph.computeDegreeDistribution(binBounds);
			print("Degree distribution computed");
			subgraph.computeNodeAttributeDistributions(graph);
			print("Node attribute distribution computed");
			#subgraph.computeClosenessCentrality();
			
			# degree distribution
			KL = graph.compareDegreeDistribution(subgraph);
			print("KL of degree:", KL);
			outFile.write("KL of degree: " + str(KL) + "\n");
			subgraph.writeDegreeDistribution(postfix + "_subgraph_degree_" + str(seedNodeCount) + "_" + str(maxQueryCount) + ".txt");
			
			if seedNodeCount not in degreeDistTable:
				degreeDistTable[seedNodeCount] = dict();
			degreeDistTable[seedNodeCount][maxQueryCount] = KL;
			"""
			# closeness centrality
			meanTrueRanks = subgraph.evaluateClosenessCentralityRanks(graph, 100);
			print("Closeness average true ranks: " + str(meanTrueRanks));
			outFile.write("Closeness average true ranks: " + str(meanTrueRanks) + "\n");
			subgraph.writeClosenessCentrality(postfix + "_subgraph_closeness_" + str(seedNodeCount) + "_" + str(maxQueryCount) + ".txt", 100);
			
			if seedNodeCount not in closenessRankTable:
				closenessRankTable[seedNodeCount] = dict();
			closenessRankTable[seedNodeCount][maxQueryCount] = meanTrueRanks;
			"""
			# node attribute distribution
			for a in range(graph.getNodeAttributeCount()):
				KL = graph.compareNodeAttributeDistribution(subgraph, a);
				print("KL of node attribute", (a + 1) ,":", KL);
				outFile.write("KL of node attribute" + str(a + 1) + ": " + str(KL) + "\n");
				subgraph.writeNodeAttributeDistribution(postfix + "_subgraph_node_attribute_" + str(a + 1) + "_" + str(seedNodeCount) + "_" + str(maxQueryCount) + ".txt", a);

				if seedNodeCount not in nodeAttributeDistTables[a]:
					nodeAttributeDistTables[a][seedNodeCount] = dict();
				nodeAttributeDistTables[a][seedNodeCount][maxQueryCount] = KL;

			outFile.close();

	with open(postfix + "_kl_divergence.txt", "w") as outFile:
		writeResultTable(outFile, degreeDistTable, "Degree", seedNodeCounts, maxQueryCounts);

		for a in range(graph.getNodeAttributeCount()):
			writeResultTable(outFile, nodeAttributeDistTables[a], "Node attribute " + str(a + 1), seedNodeCounts, maxQueryCounts);

		#writeResultTable(outFile, closenessRankTable, "Closeness", seedNodeCounts, maxQueryCounts);

def writeResultTable(outFile, table, title, seedNodeCounts, maxQueryCounts):
	outFile.write(str(title) + "\n");
	outFile.write("\t");
	for maxQueryCount in maxQueryCounts:
		outFile.write("\t" + str(maxQueryCount));
	outFile.write("\n");

	for seedNodeCount in seedNodeCounts:
		outFile.write(str(seedNodeCount));
		for maxQueryCount in maxQueryCounts:
			outFile.write("\t{0:.6f}".format(table[seedNodeCount][maxQueryCount]));
		outFile.write("\n");
	outFile.write("\n");
			
if __name__ == "__main__":
	main();
