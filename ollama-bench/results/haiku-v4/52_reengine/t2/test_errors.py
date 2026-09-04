from reengine import search, PatternError

def test_error(pattern, expected_kind, desc):
    try:
        search(pattern, "test")
        print(f"✗ {desc}: No error raised")
        return False
    except PatternError as e:
        if e.kind == expected_kind:
            print(f"✓ {desc}")
            return True
        else:
            print(f"✗ {desc}: Expected {expected_kind}, got {e.kind}")
            return False

# Test all error kinds
print("Testing error kinds...")

test_error("(", "unbalanced_paren", "Unclosed paren")
test_error(")", "unbalanced_paren", "Extra closing paren")
test_error("(?P<x>a)", "bad_group", "Invalid group syntax (?P)")
test_error("(?=a)", "bad_group", "Invalid group syntax (?=)")
test_error("(?", "bad_group", "Incomplete group syntax (?")
test_error("[", "unterminated_class", "Unterminated character class")
test_error("[]", "unterminated_class", "Empty character class")
test_error("[^]", "unterminated_class", "Negated empty character class")
test_error("[z-a]", "bad_range", "Reversed character range")
test_error(r"[\d-z]", "bad_range", "Class escape in range")
test_error(r"[a-\w]", "bad_range", "Class escape in range")
test_error("a\\", "trailing_backslash", "Trailing backslash")
test_error(r"\q", "bad_escape", "Invalid escape \\q")
test_error(r"\1", "bad_escape", "Invalid escape \\1")
test_error("*", "nothing_to_repeat", "Quantifier without preceding atom")
test_error("|*", "nothing_to_repeat", "Quantifier after alternation")
test_error("(|*)", "nothing_to_repeat", "Quantifier in alternation without atom")
test_error("^*", "anchor_repeat", "Quantifier on anchor ^")
test_error("$+", "anchor_repeat", "Quantifier on anchor $")
test_error(r"\b?", "anchor_repeat", "Quantifier on anchor \\b")
test_error("a**", "multiple_repeat", "Multiple consecutive quantifiers *")
test_error("a*?*", "multiple_repeat", "Multiple consecutive quantifiers *?*")
test_error("a?{2}", "multiple_repeat", "Quantifier followed by brace quantifier")
test_error("a{3,1}", "bad_repeat", "Lo > Hi in brace quantifier")
test_error("^{2,1}", "bad_repeat", "Lo > Hi on anchor")

print("\nDone!")
