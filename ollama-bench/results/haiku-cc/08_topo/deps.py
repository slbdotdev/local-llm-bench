import heapq
from collections import defaultdict

class CycleError(ValueError):
    """Exception raised when a cycle is detected in dependencies"""
    def __init__(self, cycle):
        self.cycle = cycle
        super().__init__(f"Cycle detected: {cycle}")

def resolve(deps: dict[str, list[str]]) -> list[str]:
    """
    Resolve dependencies and return a topological sort.

    Args:
        deps: A dict mapping nodes to their dependencies.
              deps[x] is a list of nodes that x depends on.

    Returns:
        A list of nodes in topological order (dependencies first).
        Uses alphabetical order when multiple nodes are available.

    Raises:
        CycleError: If a cycle is detected.
    """
    # Collect all nodes (including those that appear only in dependency lists)
    all_nodes = set(deps.keys())
    for dep_list in deps.values():
        all_nodes.update(dep_list)

    # Build in-degree map and adjacency list
    in_degree = {node: 0 for node in all_nodes}
    adjacency = defaultdict(list)

    for node, dep_list in deps.items():
        for dep in dep_list:
            adjacency[dep].append(node)
            in_degree[node] += 1

    # Kahn's algorithm with min-heap for deterministic ordering
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)

    result = []

    while heap:
        current = heapq.heappop(heap)
        result.append(current)

        # For each node that depends on current
        for dependent in adjacency[current]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                heapq.heappush(heap, dependent)

    # Check if all nodes were processed
    if len(result) != len(all_nodes):
        # Find a cycle
        remaining = [node for node in all_nodes if node not in result]
        cycle = _find_cycle(remaining[0], deps)
        raise CycleError(cycle)

    return result

def _find_cycle(start, deps):
    """Find a cycle using DFS"""
    visited = set()
    rec_stack = {}  # node -> position in path
    path = []

    def dfs(node):
        if node in rec_stack:
            # Found a cycle
            cycle_start_idx = rec_stack[node]
            return path[cycle_start_idx:] + [node]

        if node in visited:
            return None

        visited.add(node)
        rec_stack[node] = len(path)
        path.append(node)

        # Follow dependencies
        for dep in deps.get(node, []):
            result = dfs(dep)
            if result:
                return result

        path.pop()
        del rec_stack[node]
        return None

    return dfs(start)

if __name__ == "__main__":
    # Test 1: Basic dependencies
    result = resolve({"app": ["lib", "util"], "lib": ["util"]})
    assert result == ["util", "lib", "app"], f"Test 1 failed: {result}"
    print("Test 1 passed: Basic dependencies")

    # Test 2: Empty and single nodes (alphabetical ordering)
    result = resolve({"b": [], "a": []})
    assert result == ["a", "b"], f"Test 2 failed: {result}"
    print("Test 2 passed: Empty and single nodes")

    # Test 3: Cycle detection (2-node cycle)
    try:
        resolve({"a": ["b"], "b": ["a"]})
        assert False, "Test 3 failed: Should have raised CycleError"
    except CycleError as e:
        assert e.cycle[0] == e.cycle[-1], f"Test 3 failed: First and last must be same: {e.cycle}"
        print(f"Test 3 passed: Cycle detection - {e.cycle}")

    # Test 4: Node only in dependencies (not in keys)
    result = resolve({"b": ["a"]})
    assert result == ["a", "b"], f"Test 4 failed: {result}"
    print("Test 4 passed: Node only in dependencies")

    # Test 5: Complex graph with alphabetical ordering
    result = resolve({"c": ["a"], "b": ["a"], "a": []})
    assert result == ["a", "b", "c"], f"Test 5 failed: {result}"
    print("Test 5 passed: Complex graph with alphabetical ordering")

    # Test 6: Three-node cycle
    try:
        resolve({"a": ["b"], "b": ["c"], "c": ["a"]})
        assert False, "Test 6 failed: Should have raised CycleError"
    except CycleError as e:
        assert e.cycle[0] == e.cycle[-1], f"Test 6 failed: First and last must be same: {e.cycle}"
        print(f"Test 6 passed: Three-node cycle - {e.cycle}")

    # Test 7: Mixed dependencies with multiple sources
    result = resolve({"x": ["a", "b"], "a": ["c"], "b": ["c"], "c": []})
    assert result == ["c", "a", "b", "x"], f"Test 7 failed: {result}"
    print("Test 7 passed: Mixed dependencies with multiple sources")

    print("\nAll tests passed!")
