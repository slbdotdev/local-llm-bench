def tokenize(src: str) -> list[tuple[str, str]]:
    """
    Tokenize Python-like indented source into a stream of tokens.

    Rules:
    - Empty/whitespace-only lines and lines starting with # are ignored
    - Tabs in leading whitespace raise ValueError
    - Track indentation with a stack starting at [0]
    - Greater indentation: push and emit ("INDENT", "")
    - Smaller indentation: pop until equal, emitting ("DEDENT", "") per pop
    - Equal indentation: nothing
    - Emit ("LINE", text) with leading indent removed, comments removed, trailing whitespace stripped
    - At end: emit ("DEDENT", "") for each stack entry > 0, then ("EOF", "")
    """
    lines = src.split('\n')
    tokens = []
    stack = [0]

    for line in lines:
        # Skip empty or whitespace-only lines
        if not line or line.isspace():
            continue

        # Skip lines whose first non-space character is #
        stripped = line.lstrip()
        if stripped.startswith('#'):
            continue

        # Get indentation level (leading spaces)
        indent = len(line) - len(stripped)

        # Check for tabs in leading whitespace
        if '\t' in line[:indent]:
            raise ValueError("Tab character in leading whitespace")

        # Handle indentation changes
        top = stack[-1]
        if indent > top:
            # Increased indentation
            stack.append(indent)
            tokens.append(("INDENT", ""))
        elif indent < top:
            # Decreased indentation
            while stack and stack[-1] > indent:
                stack.pop()
                tokens.append(("DEDENT", ""))
            if not stack or stack[-1] != indent:
                raise ValueError("inconsistent dedent")

        # Remove leading indentation
        text = line[indent:]

        # Remove inline comments (but not # inside quotes)
        in_single = False
        in_double = False
        for i, char in enumerate(text):
            if char == "'" and not in_double:
                in_single = not in_single
            elif char == '"' and not in_single:
                in_double = not in_double
            elif char == '#' and not in_single and not in_double:
                text = text[:i]
                break

        # Strip trailing whitespace
        text = text.rstrip()

        tokens.append(("LINE", text))

    # Emit DEDENT for each stack entry > 0
    while len(stack) > 1:
        stack.pop()
        tokens.append(("DEDENT", ""))

    # Emit EOF
    tokens.append(("EOF", ""))

    return tokens


if __name__ == "__main__":
    # Test 1: Basic example from spec
    result = tokenize("a\n  b\n    c\n  d\ne\n")
    expected = [
        ("LINE","a"),("INDENT",""),("LINE","b"),("INDENT",""),
        ("LINE","c"),("DEDENT",""),("LINE","d"),("DEDENT",""),
        ("LINE","e"),("EOF","")
    ]
    assert result == expected, f"Test 1 failed:\nGot:      {result}\nExpected: {expected}"
    print("PASS Test 1: Basic example")

    # Test 2: Empty string
    result = tokenize("")
    expected = [("EOF", "")]
    assert result == expected, f"Test 2 failed: {result}"
    print("PASS Test 2: Empty string")

    # Test 3: Single line
    result = tokenize("hello")
    expected = [("LINE", "hello"), ("EOF", "")]
    assert result == expected, f"Test 3 failed: {result}"
    print("PASS Test 3: Single line")

    # Test 4: Lines with only comments (ignored)
    result = tokenize("# comment\na\n  # comment\n  b")
    expected = [("LINE", "a"), ("INDENT", ""), ("LINE", "b"), ("DEDENT", ""), ("EOF", "")]
    assert result == expected, f"Test 4 failed:\nGot:      {result}\nExpected: {expected}"
    print("PASS Test 4: Comment lines ignored")

    # Test 5: Empty lines ignored
    result = tokenize("a\n\n  b\n")
    expected = [("LINE", "a"), ("INDENT", ""), ("LINE", "b"), ("DEDENT", ""), ("EOF", "")]
    assert result == expected, f"Test 5 failed: {result}"
    print("PASS Test 5: Empty lines ignored")

    # Test 6: Inline comment removal
    result = tokenize("a = 1  # this is a comment")
    expected = [("LINE", "a = 1"), ("EOF", "")]
    assert result == expected, f"Test 6 failed: {result}"
    print("PASS Test 6: Inline comment removed")

    # Test 7: Comment with quotes
    result = tokenize('a = "#"  # comment')
    expected = [("LINE", 'a = "#"'), ("EOF", "")]
    assert result == expected, f"Test 7 failed: {result}"
    print("PASS Test 7: # in quotes preserved")

    # Test 8: Single quotes with #
    result = tokenize("a = '#'  # comment")
    expected = [("LINE", "a = '#'"), ("EOF", "")]
    assert result == expected, f"Test 8 failed: {result}"
    print("PASS Test 8: # in single quotes preserved")

    # Test 9: Tab raises error
    try:
        tokenize("\ta")
        assert False, "Should have raised ValueError for tab"
    except ValueError:
        print("PASS Test 9: Tab raises ValueError")

    # Test 10: Inconsistent dedent raises error
    try:
        tokenize("a\n  b\n    c\n d")  # dedent to column 1, which isn't on stack
        assert False, "Should have raised ValueError for inconsistent dedent"
    except ValueError as e:
        assert "inconsistent dedent" in str(e), f"Wrong error message: {e}"
        print("PASS Test 10: Inconsistent dedent raises ValueError")

    # Test 11: Nested quotes
    result = tokenize("x = \"it's\"  # comment")
    expected = [("LINE", "x = \"it's\""), ("EOF", "")]
    assert result == expected, f"Test 11 failed: {result}"
    print("PASS Test 11: Nested single quote in double quotes")

    # Test 12: Multiple dedents
    result = tokenize("a\n  b\n    c\nd")
    expected = [
        ("LINE", "a"), ("INDENT", ""), ("LINE", "b"), ("INDENT", ""),
        ("LINE", "c"), ("DEDENT", ""), ("DEDENT", ""), ("LINE", "d"), ("EOF", "")
    ]
    assert result == expected, f"Test 12 failed: {result}"
    print("PASS Test 12: Multiple dedents")

    print("\nAll tests passed!")
