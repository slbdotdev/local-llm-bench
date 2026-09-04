Create `roman.py` in the current directory with:

- `to_roman(n: int) -> str` for 1 <= n <= 3999 using standard subtractive notation (4 = IV, 9 = IX, 40 = XL, 90 = XC, 400 = CD, 900 = CM). Raise `ValueError` for anything outside that range or for non-int input (bool counts as non-int).
- `from_roman(s: str) -> int`: parse an uppercase Roman numeral. It must be STRICT: only accept strings that `to_roman` could have produced. Reject with `ValueError` things like `"IIII"`, `"VX"`, `"IC"`, `"XXXX"`, `"IVI"`, `"MMMM"`, `""`, lowercase, or anything with non-Roman characters. A simple way to be strict is to convert leniently and then check that `to_roman(result) == s`.

Write a few quick checks of your own and run them with `python`, then reply "done".
