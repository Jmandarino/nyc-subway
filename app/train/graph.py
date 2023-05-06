from typing import Any, DefaultDict, Dict, List, Set, Tuple

from pydantic import BaseModel


class Graph(BaseModel):

    from collections import defaultdict

    nodes: Set[Any] = set()
    edges: DefaultDict[Any, List[Tuple[Any, int]]] = defaultdict(list)

    # shortest path
    distances: Dict[Any, int] = {}
    previous: Dict[Any, Any] = {}

    def add_node(self, node):
        self.nodes.add(node)

    def add_edge(self, to_node, from_node, weight):
        self.edges[to_node].append((from_node, weight))
        self.edges[from_node].append((to_node, weight))

    def shortest_path(self, start):
        import heapq
        import sys

        visited = set()
        heap = [(0, start)]
        self.distances = {k: sys.maxsize for k in self.nodes}
        self.distances[start] = 0
        while heap:
            distance, node = heapq.heappop(heap)

            if node in visited:
                continue
            visited.add(node)

            for neighbor, weight in self.edges[node]:
                new_distance = distance + weight
                if new_distance < self.distances[neighbor]:
                    self.distances[neighbor] = new_distance
                    self.previous[neighbor] = node
                    heapq.heappush(heap, (new_distance, neighbor))

    def get_path(self, end, map):
        path = []
        while end:
            path.append(map[end])
            end = self.previous.get(end, None)
        return path[::-1]
