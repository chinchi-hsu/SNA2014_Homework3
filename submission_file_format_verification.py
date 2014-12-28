import sys;

def checkSampledGraph(filePath, returnNodes = False):
	inFile = None;
	try:
		inFile = open(filePath, "r");
	except:
		print("The file is not found");
		return False;

	nodeSet = set();

	for (index, line) in enumerate(inFile):
		row = line.strip().split();
		if len(row) != 2:
			print("It is not two numbers at line {0:d}".format(index + 1));
			return False;

		try:
			node1 = int(row[0]);
			node2 = int(row[1]);
			nodeSet.add(node1);
			nodeSet.add(node2);
		except:
			print("There is a string not a number at line {0:d}".format(index + 1));
			return False;

	return nodeSet if returnNodes else True;

def checkCloseness(filePath, graphPath):
	if graphPath != "":
		nodeSet = checkSampledGraph(graphPath, True);
		if nodeSet == False:
			return False;
	
	inFile = None;
	try:
		inFile = open(filePath, "r");
	except:
		print("The file is not found");
		return False;

	viewedDict = dict();
	nodeCount = 0;
	for (index, line) in enumerate(inFile):
		row = line.strip().split();
		
		node = None;
		try:
			node = int(row[0]);
		except:
			print("There is a string not a number at line {0:d}".format(index + 1));
			return False;

		if node not in nodeSet:
			print("The node is not in the subgraph at line {0:d}".format(index + 1));
			return False;

		if node in viewedDict:
			print("Repeated nodes: The node at line {0:d} has appeared at line {1:d}".format(index + 1, viewedDict[node] + 1));
			return False;

		viewedDict[node] = index;	
		nodeCount += 1;

	if nodeCount != 100:
		print("There is not exact 100 nodes");
		return False;

	return True;

def checkDegree(filePath):
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
	
	inFile = None;
	try:
		inFile = open(filePath, "r");
	except:
		print("The file is not found");
		return False;

	sumProbability = 0.0;
	binCount = 0;
	for (index, line) in enumerate(inFile):
		row = line.strip().split();
		if len(row) != 3:
			print("It is not three numbers at line {0:d}".format(index + 1));
			return False;
		
		lowerBound = None;
		upperBound = None;
		probability = None;
		try:
			lowerBound = int(row[0]);
			upperBound = int(row[1]);
			probability = float(row[2]);
		except:
			print("There is a string not a number at line {0:d}".format(index + 1));
			return False;
		
		binCount += 1;
		if index >= len(bins):
			break;

		if lowerBound != bins[index][0] or upperBound != bins[index][1]:
			print("The bin width does not follow the rule at line {0:d}".format(index + 1));
			return False;
		
		if probability <= 0 or probability > 1:
			print("It is not a non-zero probability at line {0:d}".format(index + 1));
			return False;

		sumProbability += probability;

	if binCount != len(bins):
		print("The number of bins should be {0:d}".format(len(bins)));
		return False;

	if sumProbability < 0.9999 or sumProbability > 1.0001:
		print("The sum of probabilities {0:f} is not 1".format(sumProbability));
		return False;

	return True;

def checkNodeAttribute(filePath, attributeIndex):
	attributeBinCount = [
			1534,
			2,
			384,
			3
	];
	
	inFile = None;
	try:
		inFile = open(filePath, "r");
	except:
		print("The file is not found");
		return False;

	sumProbability = 0.0;
	binCount = 0;
	for (index, line) in enumerate(inFile):
		row = line.strip().split();
		if len(row) != 2:
			print("It is not two numbers at line {0:d}".format(index + 1));
			return False;

		value = None;
		probability = None;
		try:
			value = int(row[0]);
			probability = float(row[1]);
		except:
			print("There is a string not a number at line {0:d}".format(index + 1));
			return False;

		if value != index:
			print("The values are not ascending at line {0:d}".format(index + 1));
			return False;
		
		if probability <= 0 or probability > 1:
			print("It is not a non-zero probability at line {0:d}".format(index + 1));
			return False;

		sumProbability += probability;
		binCount += 1;
	
	if binCount != attributeBinCount[attributeIndex]:
		print("The number of bins should be {0:d}".format(attributeBinCount[attributeIndex]));
		return False;
		
	if sumProbability < 0.9999 or sumProbability > 1.0001:
		print("The sum of probabilities {0:f} is not 1".format(sumProbability));
		return False;

	return True;

def checkFormatCase(filePath, formatType, graphPath = ""):
	if formatType == 0:
		return checkSampledGraph(filePath);
	elif formatType == 1:
		return checkDegree(filePath);
	elif formatType == 2:
		return checkCloseness(filePath, graphPath);
	elif formatType == 3:
		return checkNodeAttribute(filePath, 0);
	elif formatType == 4:
		return checkNodeAttribute(filePath, 1);
	elif formatType == 5:
		return checkNodeAttribute(filePath, 2);
	elif formatType == 6:
		return checkNodeAttribute(filePath, 3);

def reportResult(filePath, formatType, graphPath = ""):
	print("Check " + filePath + " ... ", end = "");
	if checkFormatCase(filePath, formatType, graphPath):
		print("\tOK");
	else:
		sys.exit();

def main():
	directory = sys.argv[1];
	directory = directory[: -1] if directory[-1] == "/" else directory;
	reportResult(directory + "/sample.txt", 0);
	reportResult(directory + "/degree.txt", 1);
	reportResult(directory + "/closeness.txt", 2, "sample.txt");
	reportResult(directory + "/closeness.txt", 2);
	reportResult(directory + "/node_attr_1.txt", 3);
	reportResult(directory + "/node_attr_2.txt", 4);
	reportResult(directory + "/node_attr_3.txt", 5);
	reportResult(directory + "/node_attr_4.txt", 6);

if __name__ == "__main__":
	main();

