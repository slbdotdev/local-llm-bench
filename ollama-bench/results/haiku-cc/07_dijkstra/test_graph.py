from graph import shortest_path

# Test 1: Simple path
print("Test 1: Simple path")
graph1 = {
    "a": {"b": 1, "c": 4},
    "b": {"c": 2},
    "c": {}
}
result = shortest_path(graph1, "a", "c")
print(f"  shortest_path(graph1, 'a', 'c') = {result}")
assert result == (3, ["a", "b", "c"]), f"Expected (3, ['a', 'b', 'c']), got {result}"
print("  PASS")

# Test 2: src == dst
print("\nTest 2: src == dst")
result = shortest_path(graph1, "a", "a")
print(f"  shortest_path(graph1, 'a', 'a') = {result}")
assert result == (0, ["a"]), f"Expected (0, ['a']), got {result}"
print("  PASS")

# Test 3: Unreachable destination
print("\nTest 3: Unreachable destination")
graph2 = {
    "a": {"b": 1},
    "b": {},
    "c": {"d": 1},
    "d": {}
}
result = shortest_path(graph2, "a", "d")
print(f"  shortest_path(graph2, 'a', 'd') = {result}")
assert result == (None, []), f"Expected (None, []), got {result}"
print("  PASS")

# Test 4: Direct edge
print("\nTest 4: Direct edge")
result = shortest_path(graph1, "a", "b")
print(f"  shortest_path(graph1, 'a', 'b') = {result}")
assert result == (1, ["a", "b"]), f"Expected (1, ['a', 'b']), got {result}"
print("  PASS")

# Test 5: Node only as neighbour (no outgoing edges)
print("\nTest 5: Node only as neighbour (no outgoing edges)")
graph3 = {
    "a": {"b": 5},
    "b": {"c": 3}
}
result = shortest_path(graph3, "a", "c")
print(f"  shortest_path(graph3, 'a', 'c') = {result}")
assert result == (8, ["a", "b", "c"]), f"Expected (8, ['a', 'b', 'c']), got {result}"
print("  PASS")

# Test 6: Invalid src (not in graph)
print("\nTest 6: Invalid src (not in graph)")
try:
    result = shortest_path(graph1, "z", "a")
    print(f"  ERROR: Should have raised KeyError, got {result}")
except KeyError as e:
    print(f"  Raised KeyError as expected: {e}")
    print("  PASS")

# Test 7: Multiple paths, should pick shortest
print("\nTest 7: Multiple paths, should pick shortest")
graph4 = {
    "a": {"b": 1, "c": 10},
    "b": {"c": 1},
    "c": {}
}
result = shortest_path(graph4, "a", "c")
print(f"  shortest_path(graph4, 'a', 'c') = {result}")
assert result == (2, ["a", "b", "c"]), f"Expected (2, ['a', 'b', 'c']), got {result}"
print("  PASS")

# Test 8: src is node only as neighbour
print("\nTest 8: src is node only as neighbour")
graph5 = {
    "a": {"b": 1}
}
result = shortest_path(graph5, "b", "b")
print(f"  shortest_path(graph5, 'b', 'b') = {result}")
assert result == (0, ["b"]), f"Expected (0, ['b']), got {result}"
print("  PASS")

print("\n" + "="*50)
print("All tests passed!")
