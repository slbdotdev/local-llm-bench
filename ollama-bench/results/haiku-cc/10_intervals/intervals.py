def merge(intervals):
    """Return the minimal sorted list of disjoint intervals covering the same integers.

    Overlapping AND adjacent intervals merge. E.g. (1, 3) and (4, 6) become (1, 6)
    because 3 and 4 are consecutive integers.

    Args:
        intervals: list of (start, end) tuples where start <= end

    Returns:
        Sorted list of merged disjoint intervals

    Raises:
        ValueError if any interval has start > end
    """
    if not intervals:
        return []

    # Validate all intervals
    for start, end in intervals:
        if start > end:
            raise ValueError(f"Invalid interval: start {start} > end {end}")

    # Sort intervals by start, then by end
    sorted_intervals = sorted(intervals)

    merged = [sorted_intervals[0]]

    for current_start, current_end in sorted_intervals[1:]:
        last_start, last_end = merged[-1]

        # Check if current interval overlaps or is adjacent to the last merged interval
        # Adjacent means current_start == last_end + 1
        if current_start <= last_end + 1:
            # Merge: extend the last interval
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            # No overlap/adjacency, add as new interval
            merged.append((current_start, current_end))

    return merged


def insert(intervals, new):
    """Insert a new interval into an already merged and sorted list of intervals.

    Args:
        intervals: already merged and sorted list of (start, end) tuples
        new: (start, end) tuple to insert

    Returns:
        Merged result after adding new

    Raises:
        ValueError if any interval has start > end
    """
    start, end = new
    if start > end:
        raise ValueError(f"Invalid interval: start {start} > end {end}")

    # Simply combine the existing intervals with the new one and merge
    return merge(intervals + [new])


def total_length(intervals):
    """Return the number of distinct integers covered.

    Args:
        intervals: list of (start, end) tuples where start <= end

    Returns:
        Count of distinct integers covered by all intervals

    Raises:
        ValueError if any interval has start > end
    """
    if not intervals:
        return 0

    # Validate all intervals first
    for start, end in intervals:
        if start > end:
            raise ValueError(f"Invalid interval: start {start} > end {end}")

    # Merge overlapping/adjacent intervals to get distinct coverage
    merged = merge(intervals)

    # Sum up the lengths of merged intervals
    total = 0
    for start, end in merged:
        total += end - start + 1

    return total


if __name__ == "__main__":
    # Quick tests
    print("Test 1: merge adjacent intervals")
    result = merge([(1, 3), (4, 6)])
    print(f"  merge([(1, 3), (4, 6)]) = {result}")
    assert result == [(1, 6)], f"Expected [(1, 6)], got {result}"
    print("  PASS")

    print("\nTest 2: merge overlapping intervals")
    result = merge([(1, 3), (2, 5)])
    print(f"  merge([(1, 3), (2, 5)]) = {result}")
    assert result == [(1, 5)], f"Expected [(1, 5)], got {result}"
    print("  PASS")

    print("\nTest 3: keep separate non-adjacent intervals")
    result = merge([(1, 3), (5, 6)])
    print(f"  merge([(1, 3), (5, 6)]) = {result}")
    assert result == [(1, 3), (5, 6)], f"Expected [(1, 3), (5, 6)], got {result}"
    print("  PASS")

    print("\nTest 4: empty input")
    result = merge([])
    print(f"  merge([]) = {result}")
    assert result == [], f"Expected [], got {result}"
    print("  PASS")

    print("\nTest 5: unsorted input")
    result = merge([(5, 6), (1, 3), (4, 5)])
    print(f"  merge([(5, 6), (1, 3), (4, 5)]) = {result}")
    assert result == [(1, 6)], f"Expected [(1, 6)], got {result}"
    print("  PASS")

    print("\nTest 6: invalid interval (start > end)")
    try:
        merge([(5, 2)])
        print("  FAIL: Should have raised ValueError")
    except ValueError as e:
        print(f"  Correctly raised ValueError: {e}")
        print("  PASS")

    print("\nTest 7: insert into merged intervals")
    result = insert([(1, 3), (5, 6)], (4, 7))
    print(f"  insert([(1, 3), (5, 6)], (4, 7)) = {result}")
    assert result == [(1, 7)], f"Expected [(1, 7)], got {result}"
    print("  PASS")

    print("\nTest 8: total_length with merged intervals")
    result = total_length([(1, 3), (3, 4), (10, 10)])
    print(f"  total_length([(1, 3), (3, 4), (10, 10)]) = {result}")
    assert result == 5, f"Expected 5, got {result}"
    print("  PASS")

    print("\nTest 9: total_length with empty")
    result = total_length([])
    print(f"  total_length([]) = {result}")
    assert result == 0, f"Expected 0, got {result}"
    print("  PASS")

    print("\nTest 10: total_length with single interval")
    result = total_length([(10, 15)])
    print(f"  total_length([(10, 15)]) = {result}")
    assert result == 6, f"Expected 6, got {result}"
    print("  PASS")

    print("\n" + "="*50)
    print("All tests passed!")
