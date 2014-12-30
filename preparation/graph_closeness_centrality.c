#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>

int max(int a, int b){
	return (a > b) ? a : b;
}

// ========

typedef struct{
	int *queue;
	int maxSize;
	int headIndex;
	int tailIndex;
} Queue;

Queue* newQueue(int queueMaxSize){
	Queue *queue = (Queue*)malloc(sizeof(Queue));
	queue -> maxSize = queueMaxSize;
	queue -> queue = (int*)malloc(sizeof(int) * queueMaxSize);
	queue -> headIndex = 0;
	queue -> tailIndex = 0;
	return queue;
}

void deleteQueue(Queue **queuePtr){
	if(queuePtr == NULL || *queuePtr == NULL){
		return;
	}
	Queue *queue = *queuePtr;
	free(queue -> queue);
	free(queue);
	*queuePtr = NULL;
}

void queueClear(Queue *queue, int queueMaxSize){
	if(queueMaxSize >= 0){
		queue -> queue = (int*)realloc(queue -> queue, sizeof(int) * queueMaxSize);
		queue -> maxSize = queueMaxSize;
	}
	queue -> headIndex = 0;
	queue -> tailIndex = 0;
}

bool queuePushElement(Queue *queue, int element){
	if(queue -> tailIndex == queue -> maxSize){
		return false;
	}
	queue -> queue[queue -> tailIndex] = element;
	queue -> tailIndex += 1;
	return true;
}

bool queuePopElement(Queue *queue, int *element){
	if(queue -> headIndex >= queue -> tailIndex){
		return false;
	}
	*element = queue -> queue[queue -> headIndex];
	queue -> headIndex += 1;
	return true;
}

int queueGetSize(Queue *queue){
	return queue -> tailIndex - queue -> headIndex;
}

bool queueIsEmpty(Queue *queue){
	return queueGetSize(queue) == 0;
}

void queuePrintElement(Queue *queue){
	for(int i = queue -> headIndex; i < queue -> tailIndex; i ++){
		printf(" %d", queue -> queue[i]);
	}
	printf("\n");
}


// ========

typedef struct{
	int **edges;
	int *degree;
	int maxNodeCount;
	int nodeCount;
	int edgeCount;
} Graph;

// Node ID from 1 to N
Graph *newGraph(int maxNodeCount, int nodeCount){
	Graph *graph = (Graph*)malloc(sizeof(Graph));
	graph -> edges = (int**)malloc(sizeof(int*) * (maxNodeCount + 1));
	graph -> degree = (int*)malloc(sizeof(int) * (maxNodeCount + 1));
	for(int v = 1; v <= maxNodeCount; v ++){
		graph -> edges[v] = (int*)malloc(sizeof(int));
		graph -> degree[v] = 0;
	}
	graph -> maxNodeCount = maxNodeCount;
	graph -> nodeCount = nodeCount;
	graph -> edgeCount = 0;
	return graph;	
}

void graphClear(Graph *graph, int maxNodeCount, int nodeCount){
	graph -> edges = (int**)realloc(graph -> edges, sizeof(int*) * (maxNodeCount + 1));
	graph -> degree = (int*)realloc(graph -> degree, sizeof(int) * (maxNodeCount + 1));
	for(int v = 1; v <= maxNodeCount; v ++){
		graph -> degree[v] = 0;
	}
	graph -> maxNodeCount = maxNodeCount;
	graph -> nodeCount = nodeCount;
	graph -> edgeCount = 0;
}

void deleteGraph(Graph **graphPtr){
	if(graphPtr == NULL || *graphPtr == NULL){
		return;
	}
	Graph *graph = *graphPtr;
	for(int v = 1; v <= graph -> maxNodeCount; v ++){
		free(graph -> edges[v]);
	}
	free(graph -> edges);
	free(graph -> degree);
	free(graph);
	*graphPtr = NULL;
}

void graphLoadFromFile(Graph *graph, char *filePath){
	FILE *inFile = fopen(filePath, "r");

	graphClear(graph, graph -> maxNodeCount, graph -> nodeCount);
	int node1, node2;
	while(fscanf(inFile, "%d,%d\n", &node1, &node2) == 2){
		if(node1 == node2){
			continue;
		}
		int degree1 = graph -> degree[node1];
		int degree2 = graph -> degree[node2];
		graph -> edges[node1] = (int*)realloc(graph -> edges[node1], sizeof(int) * (degree1 + 1));
		graph -> edges[node2] = (int*)realloc(graph -> edges[node2], sizeof(int) * (degree2 + 1));
		graph -> edges[node1][degree1] = node2;
		graph -> edges[node2][degree2] = node1;
		graph -> degree[node1] += 1;
		graph -> degree[node2] += 1;
		graph -> edgeCount += 1;
	}

	fclose(inFile);
}

void graphRunBFS(Graph *graph, int startNode, int *distances){
	bool* visited = (bool*)malloc(sizeof(bool) * (graph -> maxNodeCount + 1));
	for(int v = 1; v <= graph -> maxNodeCount; v ++){
		distances[v] = 0;
		visited[v] = false;
	}
	visited[startNode] = true;
	Queue *visitQueue = newQueue(graph -> nodeCount);
	queuePushElement(visitQueue, startNode);
	distances[startNode] = 0;
	//printf("BFS start: %d\n", startNode);

	while(queueIsEmpty(visitQueue) == false){
		int node;
		queuePopElement(visitQueue, &node);
		//printf("\tNode: %d\n", node);

		for(int d = 0; d < graph -> degree[node]; d ++){
			int neighbor = graph -> edges[node][d];
			//printf("\t\tNeighbor: %d\n", neighbor);
			if(visited[neighbor] == false){
				visited[neighbor] = true;
				queuePushElement(visitQueue, neighbor);
				distances[neighbor] = distances[node] + 1;
			}
		}
	}

	deleteQueue(&visitQueue);
	free(visited);
}

void evaluateNodes(char *filePath, int *maxNodeID, int *nodeCount){
	FILE *inFile = fopen(filePath, "r");
	int length = 1000;
	char line[length];
	
	*maxNodeID = 0;
	*nodeCount = 0;
	while(fgets(line, length, inFile) != NULL){
		int node;
		sscanf(line, "%d", &node);
		*nodeCount += 1;
		*maxNodeID = max(*maxNodeID, node);
	}
	
	fclose(inFile);
}

// ========

typedef struct{
	Graph *graph;
	double *scores;
} Closeness;

Closeness* newCloseness(Graph *graph){
	Closeness *closeness = (Closeness*)malloc(sizeof(Closeness));
	closeness -> graph = graph;
	closeness -> scores = (double*)malloc(sizeof(double) * (graph -> maxNodeCount + 1));
	for(int v = 1; v <= graph -> maxNodeCount; v ++){
		closeness -> scores[v] = 0.0;
	}
	return closeness;
}

void deleteCloseness(Closeness **closenessPtr){
	if(closenessPtr == NULL || *closenessPtr == NULL){
		return;
	}
	Closeness *closeness = *closenessPtr;
	free(closeness -> scores);
	free(closeness);
	*closenessPtr = NULL;
}

bool closenessRun(Closeness *closeness, int node){
	Graph *graph = closeness -> graph;
	if(node > graph -> maxNodeCount || graph -> degree[node] == 0){
		return false;
	}
	int *distances = (int*)malloc(sizeof(int) * (graph -> maxNodeCount + 1));

	graphRunBFS(graph, node, distances);
	double score = 0.0;
	for(int v = 1; v <= graph -> maxNodeCount; v ++){
		if(graph -> degree[v] > 0){
			score += distances[v];
		}
	}
	score = (graph -> nodeCount - 1) / score;
	closeness -> scores[node] = score;

	free(distances);
	return true;
}

void closenessWriteScoreToFile(Closeness *closeness, int node, FILE *outFile){
	fprintf(outFile, "%d\t%.14lf\n", node, closeness -> scores[node]);
	fflush(outFile);
}
// ========

int main(int argc, char *argv[]){
	char *nodeFilePath = argv[1];
	char *graphFilePath = argv[2];
	char *closenessFilePath = argv[3];
	int nodeFrom = atoi(argv[4]);
	int nodeTo = atoi(argv[5]);

	int maxNodeCount, nodeCount;
	evaluateNodes(nodeFilePath, &maxNodeCount, &nodeCount);
	Graph *graph = newGraph(maxNodeCount, nodeCount);
	printf("%d\t%d\n", maxNodeCount, nodeCount);
	
	graphLoadFromFile(graph, graphFilePath);
	printf("%d\t%d\n", graph -> nodeCount, graph -> edgeCount);

	FILE *closenessFile = fopen(closenessFilePath, "w");
	Closeness *closeness = newCloseness(graph);
	for(int v = nodeFrom; v <= nodeTo; v ++){
		if(closenessRun(closeness, v)){
			if(v % 100 == 0){
				printf("Node %d to %d, before node %d computed\n", nodeFrom, nodeTo, v);
				fflush(stdout);
			}
			closenessWriteScoreToFile(closeness, v, closenessFile);
		}
	}
	printf("Node %d to %d are all computed\n", nodeFrom, nodeTo);
	fflush(stdout);
	fclose(closenessFile);
	deleteCloseness(&closeness);
	deleteGraph(&graph);
	return 0;
}
