from reengine import search, PatternError

# Test basic patterns
print("Test 1: Basic literal match")
result = search("hello", "hello world")
assert result == (0, 5, []), f"Expected (0, 5, []), got {result}"
print("✓")

print("Test 2: No match")
result = search("hello", "goodbye")
assert result is None, f"Expected None, got {result}"
print("✓")

print("Test 3: Multiple starting positions")
result = search("ab", "xyzab")
assert result == (3, 5, []), f"Expected (3, 5, []), got {result}"
print("✓")

print("Test 4: Empty match")
result = search("a*", "x")
assert result == (0, 0, []), f"Expected (0, 0, []), got {result}"
print("✓")

print("Test 5: Group with empty match")
result = search("(a*)", "b")
assert result == (0, 0, [(0, 0)]), f"Expected (0, 0, [(0, 0)]), got {result}"
print("✓")

print("Test 6: Character class")
result = search("[abc]", "b")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("Test 7: Negated character class")
result = search("[^a]", "b")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("Test 8: Dot")
result = search(".", "x")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("Test 9: Dot not matching newline")
result = search(".", "\n")
assert result is None, f"Expected None, got {result}"
print("✓")

print("Test 10: Escape sequences")
result = search(r"\d", "5")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("Test 11: Non-digit escape")
result = search(r"\D", "x")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("Test 12: Word escape")
result = search(r"\w", "a")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("Test 13: Space escape")
result = search(r"\s", " ")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("Test 14: Alternation")
result = search("a|b", "b")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("Test 15: Group capture")
result = search("(x)", "x")
assert result == (0, 1, [(0, 1)]), f"Expected (0, 1, [(0, 1)]), got {result}"
print("✓")

print("Test 16: Non-capturing group")
result = search("(?:x)", "x")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("Test 17: Question mark quantifier")
result = search("a?", "x")
assert result == (0, 0, []), f"Expected (0, 0, []), got {result}"
print("✓")

print("Test 18: Plus quantifier")
result = search("a+", "aaa")
assert result == (0, 3, []), f"Expected (0, 3, []), got {result}"
print("✓")

print("Test 19: Caret anchor")
result = search("^x", "x")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("Test 20: Caret anchor fails when not at start")
result = search("^x", "yx")
assert result is None, f"Expected None, got {result}"
print("✓")

print("Test 21: Dollar anchor")
result = search("x$", "x")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("Test 22: Dollar anchor with newline")
result = search("x$", "x\n")
assert result == (0, 1, []), f"Expected (0, 1, []), got {result}"
print("✓")

print("\nAll basic tests passed!")
