from reengine import search, PatternError

print("Testing edge cases...")

# Test word boundaries
print("Test 1: Word boundary at start")
result = search(r"\b", "hello")
assert result == (0, 0, []), f"Expected (0, 0, []), got {result}"
print("✓")

print("Test 2: Word boundary in middle")
result = search(r"\b", "hello world")
assert result == (0, 0, []), f"Expected (0, 0, []), got {result}"
print("✓")

print("Test 3: Non-word boundary (space-space)")
result = search(r"\B", " x ")
# At position 1, left is space (non-word), right is 'x' (word) - word boundary
# At position 2, left is 'x' (word), right is space (non-word) - word boundary
# At position 0, left is nothing (non-word), right is space (non-word) - non-word boundary
assert result == (0, 0, []), f"Expected (0, 0, []), got {result}"
print("✓")

# Test character classes with ranges
print("Test 4: Character class with range")
result = search("[a-z]", "b")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("Test 5: Negated character class with range")
result = search("[^a-z]", "5")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

# Test escaped characters in classes
print("Test 6: Escaped dash in class")
result = search(r"[a\-z]", "-")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

# Test brace quantifiers
print("Test 7: Brace quantifier exact count")
result = search("a{3}", "aaa")
assert result == (0, 3, []), f"Expected (0, 3, []), got {result}"
print("✓")

print("Test 8: Brace quantifier range")
result = search("a{2,4}", "aaaa")
assert result == (0, 4, []), f"Expected (0, 4, []), got {result}"
print("✓")

print("Test 9: Brace quantifier min only")
result = search("a{2,}", "aaaa")
assert result == (0, 4, []), f"Expected (0, 4, []), got {result}"
print("✓")

print("Test 10: Brace quantifier max only")
result = search("a{,3}", "aaaa")
assert result == (0, 3, []), f"Expected (0, 3, []), got {result}"
print("✓")

# Test empty matches
print("Test 11: Empty alternation branch")
result = search("a|", "b")
assert result == (0, 0, []), f"Expected (0, 0, []), got {result}"
print("✓")

print("Test 12: Empty pattern")
result = search("", "anything")
assert result == (0, 0, []), f"Expected (0, 0, []), got {result}"
print("✓")

# Test multiple groups
print("Test 13: Multiple non-overlapping groups")
result = search("(a)(b)(c)", "abc")
assert result == (0, 3, [(0, 1), (1, 2), (2, 3)]), f"Expected (0, 3, [(0, 1), (1, 2), (2, 3)]), got {result}"
print("✓")

# Test groups with alternation
print("Test 14: Group with alternation - first branch matches")
result = search("(cat|dog)", "cat")
assert result == (0, 3, [(0, 3)]), f"Expected (0, 3, [(0, 3)]), got {result}"
print("✓")

print("Test 15: Group with alternation - second branch matches")
result = search("(cat|dog)", "dog")
assert result == (0, 3, [(0, 3)]), f"Expected (0, 3, [(0, 3)]), got {result}"
print("✓")

# Test group within group
print("Test 16: Nested groups")
result = search("((a))", "a")
assert result == (0, 1, [(0, 1), (0, 1)]), f"Expected (0, 1, [(0, 1), (0, 1)]), got {result}"
print("✓")

# Test group that doesn't participate
print("Test 17: Optional group that doesn't match")
result = search("a(b)?c", "ac")
assert result == (0, 2, [None]), f"Expected (0, 2, [None]), got {result}"
print("✓")

# Test literal special characters
print("Test 18: Literal brace")
result = search("a{", "a{")
assert result == (0, 2, []), f"Expected (0, 2, []), got {result}"
print("✓")

print("Test 19: Literal bracket")
result = search("a]", "a]")
assert result == (0, 2, []), f"Expected (0, 2, []), got {result}"
print("✓")

# Test escape sequences
print("Test 20: Escaped newline")
result = search(r"a\nb", "a\nb")
assert result == (0, 3, []), f"Expected (0, 3, []), got {result}"
print("✓")

print("Test 21: Escaped tab")
result = search(r"a\tb", "a\tb")
assert result == (0, 3, []), f"Expected (0, 3, []), got {result}"
print("✓")

# Test dot with different characters
print("Test 22: Dot matches letter")
result = search(".", "a")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("Test 23: Dot matches digit")
result = search(".", "5")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("Test 24: Dot matches space")
result = search(".", " ")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

# Test dollar anchor with newline edge case
print("Test 25: Dollar anchor at position before newline")
result = search("a$", "a\n")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("Test 26: Dollar anchor not at position after newline")
result = search("a$", "a\nX")
assert result is None, f"Expected None, got {result}"
print("✓")

print("\nAll edge case tests passed!")
