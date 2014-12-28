import sys;
import math;

def readDistribution(filePath):
    distribution = dict();

    for line in open(filePath, "r"):
        row = line.strip().split();

        probability = float(row[-1]);
        values = tuple([int(item) for item in row[: -1]]) if len(row[: -1]) > 1 else int(row[0]);
        distribution[values] = probability;

    return distribution;

def readClosenessRanks(filePath):
    ranks = list();
    
    for line in open(filePath, "r"):
        row = line.strip().split();

        node = int(row[0]);
        ranks.append(node);

    return ranks;

def extendedEuclidean(a, b):
    if b == 0:
        return (1, 0);
    (x, y) = extendedEuclidean(b, a % b);
    return (y, x - int(a / b) * y);

def convertNode(x, prime):
    (y, unimportantValue) = extendedEuclidean(x, prime);
    while y < 0:
        y += prime;
    while y >= prime:
        y -= prime;
    return y;

def convertListNodes(nodes, prime):
    newNodes = list();
    for node in nodes:
        newNodes.append(convertNode(node, prime));
    return newNodes;

def computeKL(distribution1, distribution2):
    kl = 0.0;

    for (value, probability1) in distribution1.items():
        if value in distribution2:
            probability2 = distribution2[value];
            kl += probability1 * math.log(probability1 / probability2);

    return kl;

def computeMeanKL(distribution1, distribution2):
    return (computeKL(distribution1, distribution2) + computeKL(distribution2, distribution1)) / 2.0;

def computeMeanRank(answerRanks, predictionRanks):
    lastRank = len(answerRanks);
    totalCount = len(predictionRanks);
    meanRank = 0.0;

    foundNodeCount = 0;
    for (i, node) in enumerate(predictionRanks):
        trueRank = lastRank;
        for (r, referenceNode) in enumerate(answerRanks):
            if node == referenceNode:
                trueRank = r + 1;
                foundNodeCount += 1;
                break;

        meanRank += trueRank;
    print("Number of found nodes:\t", foundNodeCount);

    meanRank /= totalCount;
    return meanRank;
    
def reportDegreeResult(degreeRefFilePath, degreeFilePath):
    degreeAnsDist = readDistribution(degreeRefFilePath);
    degreePreDist = readDistribution(degreeFilePath);
    degreeKL = computeMeanKL(degreeAnsDist, degreePreDist);
    print("Degree:\t\t\t", degreeKL);

def reportNodeAttributeResult(nodeAttrRefFilePath, nodeAttrFilePath, index):
    nodeAttrAnsDist = readDistribution(nodeAttrRefFilePath);
    nodeAttrPreDist = readDistribution(nodeAttrFilePath);
    nodeAttrKL = computeMeanKL(nodeAttrAnsDist, nodeAttrPreDist);
    print("Node attribute", index,":\t", nodeAttrKL);
    
def reportClosenessResult(closenessRefFilePath, closenessFilePath, prime):
    closenessAnsRanks = readClosenessRanks(closenessRefFilePath);
    closenessPreRanks = readClosenessRanks(closenessFilePath);
    closenessPreRanks = convertListNodes(closenessPreRanks, prime);
    closenessMeanRank = computeMeanRank(closenessAnsRanks, closenessPreRanks);
    print("Closeness:\t\t", closenessMeanRank);

def getPrime(team):
    teamPrime = [
        109791769,
        115968511,
        119911277,
        122947529,
        105119737,
        118870331,
        121884437,
        104878699,
        111697723,
        122947717,
        116329849,
        122948909,
        104398603,
        113510707,
        118055737,
        112785677,
        119849581,
        113867671,
        106842041,
        116905213,
        104729617,
        122946851,
        105815729,
        116267951,
        104487913,
        121581709
    ];
    return teamPrime[team - 1];

def main():
    refDirectory = "answer";
    directory = sys.argv[1];
    prime = getPrime(int(sys.argv[2]));
    directory = directory[: -1] if directory[-1] == "/" else directory;

    sampleRefFilePath = refDirectory + "/sample.txt";
    degreeRefFilePath = refDirectory + "/degree.txt";
    closenessRefFilePath = refDirectory + "/closeness.txt";
    nodeAttr1RefFilePath = refDirectory + "/node_attr_1.txt";
    nodeAttr2RefFilePath = refDirectory + "/node_attr_2.txt";
    nodeAttr3RefFilePath = refDirectory + "/node_attr_3.txt";
    nodeAttr4RefFilePath = refDirectory + "/node_attr_4.txt";

    sampleFilePath = directory + "/sample.txt";
    degreeFilePath = directory + "/degree.txt";
    closenessFilePath = directory + "/closeness.txt";
    nodeAttr1FilePath = directory + "/node_attr_1.txt";
    nodeAttr2FilePath = directory + "/node_attr_2.txt";
    nodeAttr3FilePath = directory + "/node_attr_3.txt";
    nodeAttr4FilePath = directory + "/node_attr_4.txt";

    reportClosenessResult(closenessRefFilePath, closenessFilePath, prime);
    reportDegreeResult(degreeRefFilePath, degreeFilePath);
    reportNodeAttributeResult(nodeAttr1RefFilePath, nodeAttr1FilePath, 1);
    reportNodeAttributeResult(nodeAttr2RefFilePath, nodeAttr2FilePath, 2);
    reportNodeAttributeResult(nodeAttr3RefFilePath, nodeAttr3FilePath, 3);
    reportNodeAttributeResult(nodeAttr4RefFilePath, nodeAttr4FilePath, 4);

if __name__ == "__main__":
    main();
