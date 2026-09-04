from csvfmt import write_row, read_rows, CsvError

assert write_row(["a", "b,c", 'say "hi"', ""]) == 'a,"b,c","say ""hi""",\r\n'
assert write_row(["x"], quoting="all", lineterminator="\n") == '"x"\n'
assert write_row(["a", "b"], delimiter=";") == "a;b\r\n"

assert read_rows('a,"b,c"\r\nd,"e\nf"\r\n') == [["a", "b,c"], ["d", "e\nf"]]
assert read_rows("a;b\n\nc;\n", delimiter=";") == [["a", "b"], [], ["c", ""]]

assert issubclass(CsvError, ValueError)

print("ok")
