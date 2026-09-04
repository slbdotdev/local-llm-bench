#!/usr/bin/env python3
"""Word count utility similar to Unix wc command."""

import sys
import os
from collections import defaultdict
import string


def count_file(filepath):
    """Count lines, words, and characters in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("error: no such file", file=sys.stderr)
        sys.exit(2)

    lines = content.count('\n')
    words = len(content.split())
    chars = len(content)

    return lines, words, chars


def top_words(filepath, n):
    """Find the N most frequent words in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("error: no such file", file=sys.stderr)
        sys.exit(2)

    # Extract words and clean them
    word_freq = defaultdict(int)
    tokens = content.split()

    for token in tokens:
        # Strip leading and trailing punctuation
        word = token.strip(string.punctuation).lower()
        # Skip empty strings
        if word:
            word_freq[word] += 1

    # Sort by count descending, then alphabetically for ties
    sorted_words = sorted(word_freq.items(), key=lambda x: (-x[1], x[0]))

    # Print top N (or all if fewer than N exist)
    for i, (word, count) in enumerate(sorted_words):
        if i >= n:
            break
        print(f"{word} {count}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python wc.py FILE", file=sys.stderr)
        print("       python wc.py --top N FILE", file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] == '--top':
        if len(sys.argv) < 4:
            print("Usage: python wc.py --top N FILE", file=sys.stderr)
            sys.exit(1)
        try:
            n = int(sys.argv[2])
        except ValueError:
            print("error: N must be an integer", file=sys.stderr)
            sys.exit(1)
        filepath = sys.argv[3]
        top_words(filepath, n)
    else:
        filepath = sys.argv[1]
        lines, words, chars = count_file(filepath)
        print(f"{lines} {words} {chars}")


if __name__ == '__main__':
    main()
