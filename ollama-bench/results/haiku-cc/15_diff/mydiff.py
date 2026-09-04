def diff(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """
    Compute a minimal edit script from a to b using LCS-based dynamic programming.

    Returns a list of (op, line) tuples where:
    - op "=" means the line is kept (appears in both)
    - op "-" means the line is removed from a
    - op "+" means the line is added from b

    The number of "-" and "+" operations equals len(a) + len(b) - 2 * LCS(a, b).
    """
    m, n = len(a), len(b)

    # Compute LCS length using dynamic programming
    # dp[i][j] = length of LCS of a[0:i] and b[0:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    # Backtrack to construct the edit script
    script = []
    i, j = m, n

    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i-1] == b[j-1]:
            # Match found: this line is kept
            script.append(("=", a[i-1]))
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or dp[i][j-1] >= dp[i-1][j]):
            # Need to add a line from b (prefer staying in b if tied)
            script.append(("+", b[j-1]))
            j -= 1
        else:
            # Need to delete a line from a
            script.append(("-", a[i-1]))
            i -= 1

    # Reverse since we built it backwards
    script.reverse()
    return script


def apply(a: list[str], script: list[tuple[str, str]]) -> list[str]:
    """
    Apply a diff script to list a to produce list b.

    Args:
        a: The original list
        script: A list of (op, line) tuples from diff()

    Returns:
        The resulting list after applying the script

    Raises:
        ValueError: If the script doesn't match a (mismatched lines or leftover content)
    """
    result = []
    i = 0  # Current index in a

    for op, line in script:
        if op == "=":
            # Line should be kept
            if i >= len(a) or a[i] != line:
                raise ValueError(
                    f"Script mismatch: expected '=' for line {i}, "
                    f"but got '{a[i] if i < len(a) else 'EOF'}' instead of '{line}'"
                )
            result.append(line)
            i += 1
        elif op == "-":
            # Line should be removed
            if i >= len(a) or a[i] != line:
                raise ValueError(
                    f"Script mismatch: expected '-' for line {i}, "
                    f"but got '{a[i] if i < len(a) else 'EOF'}' instead of '{line}'"
                )
            i += 1
        elif op == "+":
            # Line should be added
            result.append(line)
        else:
            raise ValueError(f"Unknown operation: '{op}'")

    # Check if we've consumed all of a
    if i < len(a):
        raise ValueError(
            f"Script did not consume all lines of a "
            f"(stopped at {i}, expected {len(a)})"
        )

    return result
