from reengine import search, PatternError

# Test greedy vs non-greedy
print("Test 1: Greedy repetition")
result = search("a+", "aaa")
assert result == (0, 3, []), f"Expected (0, 3, []), got {result}"
print("✓")

print("Test 2: Non-greedy repetition")
result = search("a+?", "aaa")
# Non-greedy should match as little as possible
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("Test 3: Group captures last iteration")
result = search("(a)+", "aaa")
# Group should capture the last 'a'
assert result == (0, 3, [(2, 3)]), f"Expected (0, 3, [(2, 3)]), got {result}"
print("✓")

print("Test 4: Complex group capture")
result = search("((a)+)", "aaa")
# Outer group should capture entire match, inner group should capture last 'a'
assert result == (0, 3, [(0, 3), (2, 3)]), f"Expected (0, 3, [(0, 3), (2, 3)]), got {result}"
print("✓")

print("Test 5: Alternation with groups")
result = search("(a)|(b)", "b")
# First group not matched, second group matched
assert result == (0, 1, [None, (0, 1)]), f"Expected (0, 1, [None, (0, 1)]), got {result}"
print("✓")

print("Test 6: Alternation - leftmost wins")
result = search("a|aa", "aa")
# Should match first branch (just 'a') at position 0
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("Test 7: Star quantifier is greedy")
result = search("a*b", "aaab")
# Should match all a's then b
assert result == (0, 4, []), f"Expected (0, 4, []), got {result}"
print("✓")

print("Test 8: Star quantifier non-greedy")
result = search("a*?b", "aaab")
# Should match minimum a's (zero) then b - but that won't work, so matches all a's
# Actually, non-greedy should try zero a's first, which fails to match b, so tries one a, etc.
# The key is that non-greedy tries the minimum first
assert result == (0, 4, []), f"Expected (0, 4, []), got {result}"
print("✓")

print("Test 9: Range quantifier")
result = search("a{2,3}", "aaaa")
# Should match 3 a's (greedy)
assert result == (0, 3, []), f"Expected (0, 3, []), got {result}"
print("✓")

print("Test 10: Range quantifier non-greedy")
result = search("a{2,3}?", "aaaa")
# Should match 2 a's (non-greedy)
assert result == (0, 2, []), f"Expected (0, 2, []), got {result}"
print("✓")

print("\nAll advanced tests passed!")
