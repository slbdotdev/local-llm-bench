Create `pathnorm.py`: purely lexical path normalisation and relativisation for two path
styles, `"posix"` and `"win"`. Everything is string work -- **no filesystem access, no
current working directory, no environment**. Two different inputs that are equal as strings
must always give equal results.

```python
class PathError(ValueError): ...   # has an attribute .kind (a str)

def normalize(path: str, style: str = "posix") -> str: ...
def relative(path: str, start: str, style: str = "posix") -> str: ...
def split_root(path: str, style: str = "posix") -> tuple[str, str]: ...
```

Do not import `os`, `os.path`, `posixpath`, `ntpath`, `pathlib` (or `genericpath`); do the
string work yourself.

## Input alphabet (everything outside it is never tested)

Every `path` / `start` argument is a `str` built only from ASCII letters `A-Za-z`, digits
`0-9`, `.`, `/`, `\` and `:`. In addition:

* In style `"posix"` the ONLY separator is `/`. A backslash `\` is an ordinary character,
  just like a letter.
* In style `"win"` BOTH `/` and `\` are separators and are completely interchangeable on
  input. A `:` only ever appears as the second character of a drive prefix.
* A "component" is a maximal run of characters containing no separator. The components
  `.` and `..` are special (see below); a component of three or more dots (`...`, `....`)
  or a name like `a.` is an ordinary name and is never altered.
* Style `"win"` inputs never begin with three or more separators, and if such an input
  begins with exactly two separators then it is a UNC path of the form
  `\\server\share` or `\\server\share<sep>...`, where `server` and `share` are non-empty
  and made of letters and digits only.
* `style` must be exactly `"posix"` or `"win"`; any other value (including a non-string)
  raises `PathError` with `.kind == "style"`. This check happens first, before anything
  else is looked at.

## `split_root(path, style)`

Splits off the *anchor* of the path and returns `(root, rest)`.

**posix.** Let `k` be the number of leading `/` characters of `path`.
`root` is `""` if `k == 0`, `"//"` if `k == 2`, and `"/"` if `k == 1` or `k >= 3`.
`rest` is `path` with all `k` leading slashes removed.

**win.** Separators in `root` are always reported as `\`; letter case is never changed.

1. If `path` begins with exactly two separators, it is UNC:
   `root` is two backslashes, then `server`, then one backslash, then `share` (that is,
   `r"\\" + server + "\\" + share` written as a Python expression), and `rest` is everything
   after the share name (so `rest` is `""` or starts with a separator).
2. Otherwise, if `path` is at least 2 characters long, `path[1] == ":"` and `path[0]` is an
   ASCII letter, then `root == path[:2]` (the drive, e.g. `"C:"`, case as written) and
   `rest == path[2:]`.
3. Otherwise `root == ""` and `rest == path`.

Note that in case 2 and 3 `rest` keeps its leading separators (if any) and its original
separator characters; only the two separators inside a UNC `root` are rewritten to `\`.

Examples:

```python
split_root("a/b",        "posix") == ("",   "a/b")
split_root("///a",       "posix") == ("/",  "a")
split_root("//a/b",      "posix") == ("//", "a/b")
split_root("C:a",        "win")   == ("C:", "a")
split_root("/a/b",       "win")   == ("",   "/a/b")
split_root("//srv/sh/a", "win")   == (r"\\srv\sh", "/a")   # root uses backslashes
split_root("//srv/sh",   "win")   == (r"\\srv\sh", "")
```

## Component resolution (shared by both styles)

Take `rest` from `split_root`, split it on runs of separators and walk the components left
to right, building an output list:

* an empty component (from a repeated or trailing separator) is dropped;
* `.` is dropped;
* `..` pops the last output component, **unless** the output list is empty or its last
  entry is itself `..`. In that case:
  * if the path is *anchored* (see below) the `..` is dropped;
  * otherwise the `..` is appended to the output list.

A path is *anchored* when it cannot go above its root: posix `root` `"/"` or `"//"`; win
UNC root; win drive root when `rest` starts with a separator (`C:\a`); win `root == ""`
when `rest` starts with a separator (`\a`). A path is NOT anchored when `root == ""` and
`rest` does not start with a separator (`a/b`), nor when the win root is a drive and `rest`
does not start with a separator (`C:a`, drive-relative) -- for those, leading `..`
components survive.

## `normalize(path, style)`

Re-join the resolved components with a single separator (`/` for posix, `\` for win):

**posix**

* `root == ""`: the components joined by `/`, or `"."` when there are none.
* `root == "/"`: `"/"` followed by the joined components (so `"/"` when there are none).
* `root == "//"`: `"//"` followed by the joined components (so `"//"` when there are none).

**win** (output always uses `\`)

* `root == ""`, `rest` does not start with a separator: joined components, or `"."` if none.
* `root == ""`, `rest` starts with a separator: `\` + joined components (so `"\"` if none).
* drive root, `rest` does not start with a separator: `root` + joined components
  (so just the drive, e.g. `"C:"`, if there are none; `"C:.."` is possible).
* drive root, `rest` starts with a separator: `root` + `\` + joined components
  (so `"C:\"` if there are none).
* UNC root and `rest == ""`: exactly `root` (e.g. `\\srv\sh`, **no** trailing separator).
* UNC root and `rest != ""`: `root` + `\` + joined components -- so a UNC path that had
  anything after the share, even just a separator, ends up with a trailing `\` when no
  components survive (e.g. `\\srv\sh\` and `\\srv\sh\a\..` both give `\\srv\sh\`).

Letter case is never changed by `normalize`.

## `relative(path, start, style)`

The lexical path from the directory `start` to `path`. Both arguments must be non-empty
strings (empty ones are never tested).

Classify each argument with `split_root`:

| class          | condition                                                  | key            |
|----------------|------------------------------------------------------------|----------------|
| `absolute`     | posix, `root` is `"/"` or `"//"`                            | `""`           |
| `relative`     | posix, `root == ""`                                        | `""`           |
| `unc`          | win, UNC root                                              | root, lowercased |
| `drive-abs`    | win, drive root, `rest` starts with a separator            | drive letter, lowercased |
| `drive-rel`    | win, drive root, `rest` does not start with a separator    | drive letter, lowercased |
| `rooted`       | win, `root == ""`, `rest` starts with a separator          | `""`           |
| `relative`     | win, `root == ""`, `rest` does not start with a separator  | `""`           |

* If the two classes differ, raise `PathError` with `.kind == "anchor"`. (So posix absolute
  vs relative, and win `drive-abs` vs `rooted`, vs `drive-rel`, vs `unc`, are all `"anchor"`.)
* Else, if the two keys differ, raise `PathError` with `.kind == "root"` (different drive
  letters, or different UNC server/share). Keys are compared case-insensitively.
* Note posix `"/x"` and `"//x"` are both class `absolute` with key `""`, so they are
  compared to each other with no error and their leading slashes are irrelevant here.

Otherwise take the resolved component lists `p` (from `path`) and `s` (from `start`), let
`k` be the length of their longest common prefix -- compared **case-insensitively** (ASCII)
for `"win"` and exactly for `"posix"` -- and return

```
("..",) * (len(s) - k) + tuple(p[k:])
```

joined with the style's separator, or `"."` when that sequence is empty. The components
taken from `p` keep the case they had in `path`.

If either resolved component list begins with a `..` (only possible for the classes
`relative` and `drive-rel`) the answer would be indeterminate; such calls are never tested.

## Visible examples

```python
normalize("a//b/./c")                == "a/b/c"
normalize("/x/y/../z/")              == "/x/z"
normalize("")                        == "."
normalize("C:/a/b/../c", "win")      == "C:\\a\\c"
relative("/a/b/c", "/a/x")           == "../b/c"
split_root("C:\\a\\b", "win")        == ("C:", "\\a\\b")
```

Write a few quick checks of your own and run them with `python`, then reply "done".
