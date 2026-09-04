Create a command-line tool `wc.py` in the current directory.

`python wc.py FILE` prints one line: `<lines> <words> <chars>` where lines = number of newline characters, words = whitespace-separated tokens, chars = number of characters (not bytes) in the file, which is UTF-8 encoded.

`python wc.py --top N FILE` instead prints the N most frequent words, one per line as `<word> <count>`. Words are lowercased and stripped of leading/trailing punctuation (`.,;:!?"'()[]`), empty results are skipped. Sort by count descending, then alphabetically for ties. If fewer than N distinct words exist, print them all.

If the file does not exist, print `error: no such file` to stderr and exit with status 2. Do not use argparse's own error output for this case.

Write a small sample file, test both modes with `python`, then reply "done".
