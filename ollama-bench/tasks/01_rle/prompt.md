Create a file `rle.py` in the current directory with two functions:

- `encode(s: str) -> str`: run-length encode a string of ASCII letters. Each run becomes the run length (decimal, may be multi-digit) followed by the character. Example: `encode("aaabccdddd") == "3a1b2c4d"`. `encode("") == ""`.
- `decode(s: str) -> str`: the exact inverse. Example: `decode("12x1y") == "xxxxxxxxxxxxy"`. `decode("") == ""`.

Write a few quick checks of your own and run them with `python`, then reply "done".
