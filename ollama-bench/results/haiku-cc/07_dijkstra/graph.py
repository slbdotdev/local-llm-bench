import heapq

def shortest_path(graph, src, dst):
    """
    Find the shortest path from src to dst using Dijkstra's algorithm.

    Args:
        graph: dict mapping node -> dict of neighbour -> edge weight (non-negative)
        src: source node
        dst: destination node

    Returns:
        tuple (cost, path) where:
        - cost: sum of edge weights (None if unreachable)
        - path: list of nodes from src to dst inclusive (empty if unreachable)

    Raises:
        KeyError: if src is not a node in the graph
    """
    # Check if src is a valid node (must be a key or appear as a neighbour)
    all_nodes = set(graph.keys())
    for neighbours in graph.values():
        all_nodes.update(neighbours.keys())

    if src not in all_nodes:
        raise KeyError(f"Source node '{src}' not in graph")

    # Handle src == dst case
    if src == dst:
        return (0, [src])

    # Initialize distances and previous node tracking
    distances = {src: 0}
    previous = {src: None}
    visited = set()

    # Min heap: (cost, node)
    heap = [(0, src)]

    while heap:
        current_cost, current_node = heapq.heappop(heap)

        # Skip if already visited
        if current_node in visited:
            continue

        visited.add(current_node)

        # If we reached the destination, reconstruct and return path
        if current_node == dst:
            path = []
            node = dst
            while node is not None:
                path.append(node)
                node = previous.get(node)
            path.reverse()
            return (current_cost, path)

        # Explore neighbours
        if current_node in graph:
            for neighbour, weight in graph[current_node].items():
                if neighbour not in visited:
                    new_cost = current_cost + weight
                    if neighbour not in distances or new_cost < distances[neighbour]:
                        distances[neighbour] = new_cost
                        previous[neighbour] = current_node
                        heapq.heappush(heap, (new_cost, neighbour))

    # Destination unreachable
    return (None, [])
