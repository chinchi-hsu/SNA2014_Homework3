import sys;
import random;
import math;

def readDistribution(filePath):
	distribution = dict();
	valueOrder = list();

	for line in open(filePath, "r"):
		row = line.strip().split();
		count = len(row);
		valueTuple = tuple([row[i] for i in range(count - 1)]);
		distribution[valueTuple] = float(row[count - 1]);
		valueOrder.append(valueTuple);

	return (valueOrder, distribution);

def computeKL(P, Q):
	kl = 0.0;

	for (v, p) in P.items():
		if v in Q:
			q = Q[v];
			kl += p * math.log(p / q);
	
	return kl;	

def computeMeanKL(distribution1, distribution2):
	return (computeKL(distribution1, distribution2) + computeKL(distribution2, distribution1)) / 2.0;

def main():
	filePath1 = sys.argv[1];
	filePath2 = sys.argv[2];

	(valueOrder1, distribution1) = readDistribution(filePath1);
	(valueOrder2, distribution2) = readDistribution(filePath2);
	print(computeMeanKL(distribution1, distribution2));

if __name__ == "__main__":
	main();
