from reengine import search, PatternError

print("Testing more edge cases...")

# Test complex patterns
print("Test 1: Complex pattern with multiple quantifiers")
result = search(r"(\d+)-(\d+)", "test123-456end")
assert result == (4, 11, [(4, 7), (8, 11)]), f"Got {result}"
print("✓")

print("Test 2: Pattern with repeated alternation")
result = search("(a|b)(a|b)", "ab")
assert result == (0, 2, [(0, 1), (1, 2)]), f"Got {result}"
print("✓")

print("Test 3: Greedy backtracking complex")
result = search("a.*b", "axxxbxxxb")
# a matches first char, .* greedily matches "xxxbxxx", final b matches last char
assert result == (0, 9, []), f"Got {result}"
print("✓")

print("Test 4: Non-greedy backtracking complex")
result = search("a.*?b", "axxxbxxxb")
# a matches first char, .*? matches "xxx" (minimum to reach first b), final b matches
assert result == (0, 5, []), f"Got {result}"
print("✓")

print("Test 5: Pattern with optional groups")
result = search("(a)(b)?(c)", "ac")
assert result == (0, 2, [(0, 1), None, (1, 2)]), f"Got {result}"
print("✓")

print("Test 6: Character class with multiple ranges")
result = search("[a-zA-Z0-9_]", "A")
assert result == (0, 1, []), f"Got {result}"
print("✓")

print("Test 7: Dollar at end of line")
result = search("x$", "x\n")
assert result == (0, 1, []), f"Got {result}"
print("✓")

print("Test 8: Multiple empty groups")
result = search("()()", "")
assert result == (0, 0, [(0, 0), (0, 0)]), f"Got {result}"
print("✓")

print("Test 9: Alternation with empty branch first")
result = search("(|a)", "a")
assert result == (0, 0, [(0, 0)]), f"Got {result}"
print("✓")

print("Test 10: Alternation with empty branch second")
result = search("(a|)", "")
assert result == (0, 0, [(0, 0)]), f"Got {result}"
print("✓")

print("Test 11: Negated class with digit")
result = search("[^0-9]", "a")
assert result == (0, 1, []), f"Got {result}"
print("✓")

print("Test 12: Multiple consecutive anchors")
result = search("^", "test")
assert result == (0, 0, []), f"Got {result}"
print("✓")

print("Test 13: Word boundary in middle")
result = search(r"\bhello\b", "  hello  ")
assert result == (2, 7, []), f"Got {result}"
print("✓")

print("Test 14: Complex nesting")
result = search("((a)+)+b", "aaab")
assert result == (0, 4, [(0, 3), (2, 3)]), f"Got {result}"
print("✓")

print("Test 15: Greedy with immediate boundary")
result = search("a*$", "aaa")
assert result == (0, 3, []), f"Got {result}"
print("✓")

print("Test 16: Empty match at boundary")
result = search("a*", "")
assert result == (0, 0, []), f"Got {result}"
print("✓")

print("Test 17: Character class with ] literal")
result = search(r"[\]]", "]")
assert result == (0, 1, []), f"Got {result}"
print("✓")

print("Test 18: Character class with - at start")
result = search(r"[-a]", "-")
assert result == (0, 1, []), f"Got {result}"
print("✓")

print("Test 19: Character class with - at end")
result = search(r"[a-]", "-")
assert result == (0, 1, []), f"Got {result}"
print("✓")

print("Test 20: Escaped special char in pattern")
result = search(r"\.", ".")
assert result == (0, 1, []), f"Got {result}"
print("✓")

print("\nAll additional edge case tests passed!")
