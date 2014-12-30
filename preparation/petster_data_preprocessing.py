import networkx;
import sys;

def removeQuotes(row):
	newRow = ["" for i in range(len(row))];

	for i in range(len(row)):
		newRow[i] = row[i].strip();

		if len(newRow[i]) > 0 and newRow[i][0] == "\"":
			newRow[i] = newRow[i][1 : ];

		if len(newRow[i]) > 0 and newRow[i][-1] == "\"":
			newRow[i] = newRow[i][ : -1];

		newRow[i] = newRow[i].strip();

	return newRow;

def convertLowercase(row):
	newRow = ["" for i in range(len(row))];

	for i in range(len(row)):
		newRow[i] = row[i].lower();

	return newRow;

def changeState(state, pointer):
	if state == 1:
		if pointer == "\"":
			return 2;

		elif pointer in [" ", "\n", "\t"]:
			return 4;

		else:
			return 1;

	elif state == 2:
		if pointer == "\\":
			return 3;

		elif pointer == "\"":
			return 1;

		else:
			return 2;

	elif state == 3:
		return 2;

	elif state == 4:
		if pointer in [" ", "\n", "\t"]:
			return 4;

		elif pointer == "\"":
			return 2;

		else:
			return 1;

def generateRow(line):
	line = line;
	row = [];
	state = 1;
	startIndex = 0;

	for (i, character) in enumerate(line):
		oldState = state;
		state = changeState(state, character);

		if oldState == 1 and state != 1:		# non-space terminates
			row.append(line[startIndex : i]);

		elif oldState == 4 and state != 4:						# previous character is a space
			startIndex = i;

	return row;

def readAttributes(filePath, attributeColumnDict, nodeWord):
	data = list();

	with open(filePath, "r") as inFile:
		inFile.readline();
		inFile.readline();
		inFile.readline();

		for line in inFile:
			row = convertLowercase(removeQuotes(generateRow(line)));

			if len(row[attributeColumnDict[nodeWord]]) == 0:
				continue;

			data.append(dict());
			for (attribute, columnIndex) in attributeColumnDict.items():
				value = row[columnIndex];
				if attribute == nodeWord:
					value = int(value);
				data[-1][attribute] = value;

	return data;

def writeAttributes(filePath, data, attributeColumnDict, nodeWord, keptWord):
	with open(filePath, "w") as outFile:
		for row in sorted(data, key = lambda row: row[nodeWord]):
			if row[keptWord]:
				for (attribute, columnIndex) in sorted(attributeColumnDict.items(), key = lambda item: item[1]):
					outFile.write(str(row[attribute]) + "\t");
				outFile.write("\n");

def processSpecies(data, speciesWord, keptWord):
	speciesDict = dict();
	count = 0;

	for row in data:
		if row[keptWord]:
			species = row[speciesWord];

			if species not in speciesDict:
				speciesDict[species] = count;
				count += 1;
			row[speciesWord] = speciesDict[species];

	return speciesDict;

def processSex(data, sexWord, keptWord):
	sexDict = dict();
	count = 0;

	for row in data:
		if row[keptWord]:
			sex = row[sexWord];

			if sex not in sexDict:
				sexDict[sex] = count;
				count += 1;
			row[sexWord] = sexDict[sex];

	return sexDict;

def processHome(data, homeWord, keptWord):
	homeDict = dict();
	count = 0;

	for row in data:
		if row[keptWord]:
			home = row[homeWord];
			
			if home != "":
				home = home.split()[-1];
				home = home.split(",")[-1];
				home = home.split("/")[-1];
				home = home.strip();
				
			if home not in homeDict:
				homeDict[home] = count;
				count += 1;
			row[homeWord] = homeDict[home];

	return homeDict;

def processRace(data, raceWord, keptWord):
	raceDict = dict();
	count = 0;

	for row in data:
		if row[keptWord]:
			race = row[raceWord];

			if race != "":
				racePair = race.split("/");
				race1 = min([racePair[0], racePair[-1]]).strip();
				race2 = max([racePair[0], racePair[-1]]).strip();
				race = race1;

			if race not in raceDict:
				raceDict[race] = count;
				count += 1;
			row[raceWord] = raceDict[race];

	return raceDict;

def getAttributeSet(data, attribute):
	attributeSet = set();

	for row in data:
		attributeSet.add(row[attribute]);
	
	return attributeSet;

def keepDataRows(data, graph, nodeWord, keptWord):
	for row in data:
		node = row[nodeWord];
		row[keptWord] = graph.has_node(node);

def removeMaxDegreeNodes(graph, nodeCount):
	removedNodes = sorted(graph.nodes(), key = graph.degree, reverse = True)[ : nodeCount];
	graph.remove_nodes_from(removedNodes);

def readGraph(filePath, nodeSet):
	graph = networkx.Graph();

	with open(filePath, "r") as inFile:
		inFile.readline();

		for line in inFile:
			row = line.strip().split();
			node1 = int(row[0]);
			node2 = int(row[1]);
			if node1 in nodeSet and node2 in nodeSet and node1 != node2:
				graph.add_edge(node1, node2);

	return graph;

def writeGraph(filePath, graph):
	with open(filePath, "w") as outFile:
		for (node1, node2) in sorted(graph.edges()):
			outFile.write(str(node1) + "\t" + str(node2) + "\n");
			
def main():
	attributeFilePath = sys.argv[1];
	relationFilePath = sys.argv[2];
	nodeFilePath = sys.argv[3];
	edgeFilePath = sys.argv[4];

	print("Read data");
	keptWord = "kept";
	nodeWord = "node";
	homeWord = "home";
	sexWord = "sex";
	raceWord = "race";
	speciesWord = "species";
	attributeColumnDict = {nodeWord: 0, homeWord: 2, sexWord: 4, raceWord: 5, speciesWord: 6};
	data = readAttributes(attributeFilePath, attributeColumnDict, nodeWord);
	
	print("Process graph");
	nodeSet = getAttributeSet(data, nodeWord);
	print("#node:", len(nodeSet));
	graph = readGraph(relationFilePath, nodeSet);
	removeMaxDegreeNodes(graph, 3000);
	graph = max(networkx.connected_component_subgraphs(graph), key = lambda g: g.number_of_nodes());
	keepDataRows(data, graph, nodeWord, keptWord);
	
	print("Process data");
	homeDict = processHome(data, homeWord, keptWord);
	sexDict = processSex(data, sexWord, keptWord);
	raceDict = processRace(data, raceWord, keptWord);
	speciesDict = processSpecies(data, speciesWord, keptWord);

	print("Write data");
	print("#data:", len(data));
	print();
	print("home:", sorted(homeDict.items(), key = lambda item: item[1]), "#home:", len(homeDict), "space:", homeDict['']);
	print();
	print("sex:", sorted(sexDict.items(), key = lambda item: item[1]));
	print();
	print("race:", sorted(raceDict.items(), key = lambda item: item[1]), "#race:", len(raceDict), "space:", raceDict['']);
	print();
	print("species:", sorted(speciesDict.items(), key = lambda item: item[1]));
	print();
	print("Graph:", graph.number_of_nodes(), graph.number_of_edges());
	print("Connected:", networkx.is_connected(graph));

	writeAttributes(nodeFilePath, data, attributeColumnDict, nodeWord, keptWord);
	writeGraph(edgeFilePath, graph);	

if __name__ == "__main__":
	main();
