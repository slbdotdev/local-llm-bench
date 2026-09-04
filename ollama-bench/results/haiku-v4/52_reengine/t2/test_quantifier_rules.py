from reengine import search, PatternError

print("Testing quantifier rules...")

# Test the rule: "A mandatory iteration is allowed to consume no characters"
print("Test 1: Mandatory empty iteration")
result = search("(a*)b", "b")
assert result == (0, 1, [(0, 0)]), f"Expected (0, 1, [(0, 0)]), got {result}"
print("✓")

# Test the rule: "if the previous iteration consumed nothing, no further iteration is attempted"
print("Test 2: No continuation after empty iteration in optional")
result = search("a*", "b")
assert result == (0, 0, []), f"Expected (0, 0, []), got {result}"
print("✓")

# Test nested repetitions
# The outer + does 1 iteration where (a+) matches all 3 a's
print("Test 3: Nested repetitions")
result = search("(a+)+", "aaa")
assert result == (0, 3, [(0, 3)]), f"Expected (0, 3, [(0, 3)]), got {result}"
print("✓")

# Test the rule about empty matches not continuing
print("Test 4: Star with empty match stops")
result = search("(a|)+", "a")
assert result == (0, 1, [(0, 1)]), f"Expected (0, 1, [(0, 1)]), got {result}"
print("✓")

# Test alternation ordering (leftmost first)
print("Test 5: Alternation - leftmost wins over longer")
result = search("abc|abcdef", "abcdef")
assert result == (0, 3, []), f"Expected (0, 3, []), got {result}"
print("✓")

# Test greedy vs non-greedy with remainder
print("Test 6: Greedy with remainder requiring backtracking")
result = search("a*ab", "aaab")
assert result == (0, 4, []), f"Expected (0, 4, []), got {result}"
print("✓")

# Test greedy matching the maximum
print("Test 7: Greedy matches maximum with no remainder")
result = search("a*", "aaa")
assert result == (0, 3, []), f"Expected (0, 3, []), got {result}"
print("✓")

# Test non-greedy matching the minimum
print("Test 8: Non-greedy matches minimum with no remainder")
result = search("a*?", "aaa")
assert result == (0, 0, []), f"Expected (0, 0, []), got {result}"
print("✓")

# Test group capture in nested quantifiers
# Outer group captures entire body, inner group captures last iteration of a+
print("Test 9: Group in nested quantifier captures last")
result = search("((a)+)+", "aaa")
assert result == (0, 3, [(0, 3), (2, 3)]), f"Expected (0, 3, [(0, 3), (2, 3)]), got {result}"
print("✓")

# Test multiple groups with backtracking
print("Test 10: Multiple groups with backtracking")
result = search("(a+)(a+)", "aaa")
assert result == (0, 3, [(0, 2), (2, 3)]), f"Expected (0, 3, [(0, 2), (2, 3)]), got {result}"
print("✓")

# Test the constraint about empty repetitions
print("Test 11: Empty repetition in loop stops")
result = search("(a*b)*", "b")
assert result == (0, 1, [(0, 1)]), f"Expected (0, 1, [(0, 1)]), got {result}"
print("✓")

# Test character classes with special escape
print("Test 12: Class with \\w")
result = search(r"[\w]", "a")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

# Test character class with digit escape
print("Test 13: Class with \\d")
result = search(r"[\d]", "5")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

# Test class with space escape
print("Test 14: Class with \\s")
result = search(r"[\s]", " ")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

# Test negated class with escape
print("Test 15: Negated class with \\w")
result = search(r"[^\w]", " ")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

# Test first matching position (leftmost)
print("Test 16: Leftmost position")
result = search("ab", "xyzabdef")
assert result == (3, 5, []), f"Expected (3, 5, []), got {result}"
print("✓")

# Test empty match at leftmost position
print("Test 17: Empty match at leftmost position")
result = search("a*", "bbb")
assert result == (0, 0, []), f"Expected (0, 0, []), got {result}"
print("✓")

# Test matching at each position
print("Test 18: Matching at second position")
result = search("b", "ab")
assert result == (1, 2, []), f"Expected (1, 2, []), got {result}"
print("✓")

print("\nAll quantifier rule tests passed!")
