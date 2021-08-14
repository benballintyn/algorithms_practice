import warnings
from queue import SimpleQueue, PriorityQueue

class Graph:
    def __init__(self,isDirected,**kwargs):
        self.nodeList = []
        self.edges = {}
        self.nodeNames = {}
        self.isDirected = isDirected
        self.isWeighted = False
        self.n = 0
        # If an edge list was provided, read it into the graph
        for key, value in kwargs.items():
            if key == 'edgeList':
                for edge in value:
                    # If the source of the edge is not in the graph, add it
                    if not edge[0] in self.nodeNames:
                        self.addNode(str(edge[0]),[])

                    # If the target of the edge is not in the graph, add it
                    if not edge[1] in self.nodeNames:
                        self.addNode(str(edge[1]),[])

                    # Add the edge with an optional given weight (1 default)
                    if len(edge) == 2:
                        self.addEdge(edge[0],edge[1],weight=1)
                    elif len(edge) == 3:
                        self.addEdge(edge[0],edge[1],weight=edge[2])
                    else:
                        raise EdgeListNumberError()

    def addNode(self,name,edges):
        # 
        if name in self.nodeNames.values():
            raise DuplicateNodeNameError(f'Node {name} already exists in the\
                                         graph')
        else:
            self.nodeList.append(self.n)
            self.edges[self.n] = {}
            for edge in edges:
                if len(edge) == 1:
                    self.addEdge(self.n,edge[0],1)
                else:
                    self.addEdge(self.n,edge[0],edge[1])
            self.nodeNames[self.n] = name
            self.n += 1

        if not self.isDirected:
            for edge in edges:
                if (edge[0] > self.n - 1):
                    self.nodeList.pop(self.n - 1)
                    self.edges.pop(self.n - 1)
                    self.nodeNames.pop(self.n - 1)
                    self.n -= 1
                    raise NodeNotFoundError(f'Node {edge} is not in the graph yet')
                else:
                    self.addEdge(edge[0],self.n-1)

    def addEdge(self,src,tgt,**kwargs):
        if (src > self.n - 1):
            raise NodeNotFoundError(f'Node {src} is not in the graph yet')
        elif (tgt > self.n - 1):
            raise NodeNotFoundError(f'Node {tgt} is not in the graph yet')
        else:
            if tgt not in self.edges[src]:
                if 'weight' in kwargs:
                    self.edges[src][tgt] = kwargs['weight']
                else:
                    self.edges[src][tgt] = 1
            else:
                warnings.warn('Edge {src} --> {tgt} already exists')

    def removeNode(self,nodeIndex):
        self.nodeNames.pop(nodeIndex)
        self.nodeList.pop(nodeIndex)
        self.edges.pop(nodeIndex)

        for node,edgeDict in self.edges.items():
            if nodeIndex in edgeDict:
                edgeDict.pop(nodeIndex)
        self.n -= 1

    def topological_sort(self):
        # Check to make sure graph is directed
        if not self.isDirected:
            raise NoTopoSortOnUndirectedGraphError()
        # Check to make sure graph is acyclic
        elif self.has_cycle():
            raise NoTopoSortOnCyclicGraphError()
        # If checks pass, do topological sort
        else:
            order = SimpleQueue() # Queue to store topological sort order
            processNext = SimpleQueue() # Queue to store nodes to process next
            nIncoming = [0]*self.n # 'Array' to hold number of incoming edges
            # Count number of incoming edges for each node
            for node in self.nodeList:
                for edge in self.edges[node]:
                    nIncoming[edge] += 1
            # Add all nodes with no incoming edges to processNext
            for node in self.nodeList:
                if nIncoming[node] == 0:
                    processNext.put(node)

            while not processNext.empty():
                curNode = processNext.get()
                for tgt in self.edges[curNode]:
                    nIncoming[tgt] -= 1
                    if nIncoming[tgt] == 0:
                        processNext.put(tgt)

                order.put(curNode)
            
            return order

    def has_cycle(self):
        if not self.isDirected:
            raise AllUndirectedGraphsHaveCyclesError()
        discovered = set()
        finished = set()
        for node in self.nodeList:
            if node not in discovered and node not in finished:
                discovered, finished, cycle_detected = self.dfs_visit(node,discovered,finished)
                if cycle_detected:
                    return True

        return False

    def dfs_visit(self,node,discovered,finished):
        discovered.add(node)
        cycle_detected = False
        for tgt,weight in self.edges[node].items():
            if tgt in discovered:
                cycle_detected = True
                return discovered, finished, cycle_detected
            elif tgt not in finished:
                discovered, finished, cycle_detected = self.dfs_visit(tgt,discovered,finished)

        discovered.remove(node)
        finished.add(node)
        return discovered, finished, cycle_detected

    def dijkstra(self,start):
        """Implementation of Dijkstra's algorithm to find all shortest paths
        from a given node"""
        path_weight = {i : float('inf') for i in range(self.n)}
        path_weight[start] = 0
        previous = {i : float('nan') for i in range(self.n)}
        remaining = PriorityQueue()
        for node,priority in path_weight.items():
            remaining.put((priority,node))

        while not remaining.empty():
            priority,node = remaining.get()
            for tgt,weight in self.edges[node].items():
                possibleNewWeight = path_weight[node] + weight
                if (possibleNewWeight < path_weight[tgt]):
                    path_weight[tgt] = possibleNewWeight
                    previous[tgt] = node
        
        return path_weight, previous
        


class GraphError(Exception):
    """Base class for exceptions in the Graph module."""
    pass

class NodeNotFoundError(GraphError):
    """Exception raised when a edge to a non-existent node is being added"""

    def __init__(self,message):
        self.message = message

class DuplicateNodeNameError(GraphError):
    """Exception raised when a node is added with a name of an existing node"""

    def __init__(self,message):
        self.message = message

class NoTopoSortOnUndirectedGraphError(GraphError):

    def __init__(self):
        self.message = 'Topological sort does not work on undirected graphs.'

class NoTopoSortOnCyclicGraphError(GraphError):

    def __init__(self):
        self.message = 'Topological sort does not work on cyclic graphs.'

class AllUndirectedGraphsHaveCyclesError(GraphError):

    def __init__(self):
        self.message = 'All undirected graphs have cycles.'

class EdgeListNumberError(GraphError):

    def __init__(self):
        self.message = 'Edges in list given to __init__ must be tuples of\
        length 2 or 3'
