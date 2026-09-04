Create `uriref.py` in the current directory: an RFC-3986-style URI reference parser,
normalizer and resolver, as pure string processing. Standard library only, and you must
**not** import (directly or indirectly, in any form) any of `re`, `urllib`,
`urllib.parse`, `posixpath`, `ipaddress`, `string`, `binascii`. A correct solution needs
no imports at all.

The module must define exactly this API:

- `UriError` — an exception class you define. It must be a subclass of `ValueError`, and
  every instance you raise must carry an attribute `.kind` holding one of the exact
  strings listed below (`"type"`, `"scheme"`, `"port"`, `"host"`, `"userinfo"`, `"char"`,
  `"escape"`, `"form"`, `"base"`). Every rejection below raises `UriError` with the stated
  kind — never a bare `ValueError`, never a silent fallback or a repaired result.
- `parse(s)` → `dict`
- `unparse(d)` → `str`
- `normalize(s)` → `str`
- `resolve(base, ref)` → `str`

## Character sets

- ALPHA = `A`-`Z` `a`-`z`; DIGIT = `0`-`9`; HEXDIG = `0`-`9` `A`-`F` `a`-`f`.
- unreserved = ALPHA / DIGIT / `-` / `.` / `_` / `~`
- sub-delims = `!` `$` `&` `'` `(` `)` `*` `+` `,` `;` `=`
- The characters allowed in each component are:
  - host: unreserved / sub-delims / `%`
  - userinfo: the host set plus `:`
  - path: the userinfo set plus `@` and `/`
  - query and fragment: the path set plus `?`
  - port: DIGIT only

  IP-literals (`[::1]`) are not supported: `[` and `]` are simply not allowed anywhere.

## `parse(s)`

Returns a `dict` with **exactly** these seven keys: `"scheme"`, `"userinfo"`, `"host"`,
`"port"`, `"path"`, `"query"`, `"fragment"`. Every value is a `str` or `None`; `"path"` is
always a `str` (possibly `""`). `None` means the component is **absent**; `""` means it is
**present and empty** — these are different, and must never be confused. `parse` performs
no normalization whatsoever: components are returned exactly as they appear in `s`.

Splitting, in this order:

1. If `s` is not a `str`, raise kind `"type"`.
2. If `s` contains `#`, the fragment is everything after the **first** `#` and the rest of
   the work happens on the part before it; otherwise the fragment is `None`.
3. If what is left contains `?`, the query is everything after the **first** `?` and work
   continues on the part before it; otherwise the query is `None`.
4. Let `c` be the index of the first `:` in what is left and `l` the index of the first
   `/`. If a `:` exists and (there is no `/` or `c < l`), the text before that `:` is the
   scheme: it must match `ALPHA *( ALPHA / DIGIT / "+" / "-" / "." )`, otherwise raise
   kind `"scheme"`. Remove the scheme and the `:`. Otherwise the scheme is `None`.
5. If what is left starts with `//`, an authority is present: it is the text after those
   two slashes up to (not including) the next `/`, and the path is the remainder starting
   at that `/` (or `""` if there is no further `/`). Otherwise the authority is absent
   (`"host"` is `None`) and the path is all of what is left.
6. Split the authority: if it contains `@`, the userinfo is the text before the **last**
   `@` and the host-port is the text after it; otherwise the userinfo is `None`. If the
   host-port contains `:`, the host is the text before the **last** `:` and the port is
   the text after it; otherwise the port is `None`. So `//` gives host `""`, userinfo
   `None`, port `None`; `//@` gives userinfo `""` and host `""`; `//:` gives host `""` and
   port `""`.

Validation then runs in **exactly this order**, and the first check that fails decides the
kind (later checks are not reached):

1. `"type"` — as in step 1 above.
2. `"scheme"` — as in step 4 above.
3. `"port"` — the port is present and contains a character that is not a DIGIT.
4. `"host"` — the host contains a character outside the host set.
5. `"userinfo"` — the userinfo is present and contains a character outside the userinfo set.
6. `"char"` — the path, query or fragment (in that order) contains a character outside its
   set. Note `%` is in every one of those sets, so a `%` never fails this check.
7. `"escape"` — somewhere in `s` there is a `%` that is not followed by two HEXDIG
   characters (`"%"`, `"%A"`, `"%GG"`, `"%zz"`). Scan left to right, skipping three
   characters past each well-formed escape.

## `unparse(d)`

Rebuilds the string from a component dict, without validating the contents of the
components. Checks, in **exactly this order**:

1. `d` is not a `dict` → kind `"type"`.
2. `set(d)` is not exactly the seven key names → kind `"form"`.
3. some value is neither a `str` nor `None` → kind `"type"`.
4. structural problems → kind `"form"`: `"path"` is `None`; or the host is `None` while
   the userinfo or the port is not `None`; or the host is not `None` while the path is
   neither `""` nor starting with `/`; or the host is `None` while the path starts with
   `//`; or the scheme and the host are both `None` while the first segment of the path
   (the text before its first `/`, or the whole path if it has none) contains a `:`.
   (The last three would otherwise produce a string that parses back differently.)

Otherwise the result is the concatenation of: the scheme and `:` if the scheme is not
`None`; then, if the host is not `None`, `//` plus the userinfo and `@` if the userinfo is
not `None`, plus the host, plus `:` and the port if the port is not `None`; then the path;
then `?` and the query if the query is not `None`; then `#` and the fragment if the
fragment is not `None`. Consequently `unparse(parse(x)) == x` for every `x` that `parse`
accepts.

## `remove_dot_segments(path)`

Used below; you need not export it. With `in` = the input and `out` = `""`, loop while
`in` is non-empty and apply the **first** rule that applies:

- A. `in` starts with `../` → drop those 3 characters; else `in` starts with `./` → drop
  those 2.
- B. `in` starts with `/./` → replace that prefix by `/`; else `in` is exactly `/.` →
  `in` becomes `/`.
- C. `in` starts with `/../` → replace that prefix by `/` **and** remove the last segment
  of `out` (delete everything from its last `/` onwards; if `out` has no `/`, `out`
  becomes `""`); else `in` is exactly `/..` → same, with `in` becoming `/`.
- D. `in` is exactly `.` or `..` → `in` becomes `""`.
- E. otherwise move the first segment of `in` to the end of `out`: that is the leading
  `/` if present plus everything up to (not including) the next `/`.

Return `out`. Empty segments are never collapsed: `a//b` stays `a//b`.

## `normalize(s)`

`parse` the string (so all of its errors propagate unchanged), then apply these steps in
order and serialize with the `unparse` rules:

1. The scheme is lowercased (ASCII `A`-`Z` only).
2. Percent-escapes are canonicalized in the userinfo, host, path, query and fragment,
   each independently: for each `%XY`, uppercase the two hex digits; then, if `chr(0xXY)`
   is an **unreserved** character, replace the whole escape by that character; otherwise
   keep it as `%XY` with uppercase hex. Characters that are not part of an escape are
   never encoded and never decoded. So `%2f` stays `%2F` (a `/` is not unreserved) and
   `%7e` becomes `~`.
3. In the host only, after step 2, every ASCII letter that is **not** part of a remaining
   percent-escape is lowercased (so `%41` becomes `A` in step 2 and then `a`, while `%C3`
   stays `%C3`). The userinfo, path, query and fragment are never case-folded.
4. Port: an empty port becomes absent (`None`), so `//h:` normalizes to `//h`. Otherwise
   the port is rewritten as its decimal value without leading zeros (`080` → `80`,
   `00` → `0`); if the (lowercased) scheme is `http` or `ws` and that value is `80`, or
   the scheme is `https` or `wss` and that value is `443`, the port becomes absent. No
   other scheme has a default port.
5. If the host is not `None`, or the path starts with `/`, the path is replaced by
   `remove_dot_segments(path)`; otherwise the path is left alone (a relative path such as
   `a/../b` keeps its dot segments). An empty path stays empty: `http://h` does **not**
   grow a `/`.
6. Recomposition guard: if the host is `None` and the path now starts with `//`, prefix
   the path with `/.`.

## `resolve(base, ref)`

1. If either argument is not a `str`, raise kind `"type"`.
2. `parse(base)` (errors propagate). If it has no scheme, raise kind `"base"`. Only then
   is `ref` parsed (so a bad `ref` never masks a relative `base`).
3. Compute the target components T from B (= parsed base) and R (= parsed ref), strictly:
   - if R has a scheme: T's scheme, userinfo, host, port and query are R's, and T's path
     is `remove_dot_segments(R.path)`;
   - else if R's host is not `None`: T's userinfo, host, port and query are R's, T's path
     is `remove_dot_segments(R.path)`, and T's scheme is B's;
   - else T's userinfo, host, port are B's and T's scheme is B's, and:
     - if R's path is `""`: T's path is B's path, and T's query is R's query if that is
       not `None`, else B's query;
     - else T's query is R's query, and T's path is `remove_dot_segments(R.path)` if R's
       path starts with `/`, otherwise `remove_dot_segments(merge(B, R))`, where
       `merge(B, R)` is `"/" + R.path` when B has a host and B's path is `""`, and
       otherwise B's path up to and including its last `/` (or `""` if it has none)
       followed by R's path.
   - T's fragment is always R's fragment.
4. Apply steps 1-6 of `normalize` to T and serialize it. So `resolve` always returns a
   fully normalized absolute URI.

Examples:

```python
parse("http://a.com/x?y=1#z") == {"scheme": "http", "userinfo": None, "host": "a.com",
    "port": None, "path": "/x", "query": "y=1", "fragment": "z"}
parse("mailto:x@y") == {"scheme": "mailto", "userinfo": None, "host": None, "port": None,
    "path": "x@y", "query": None, "fragment": None}
unparse(parse("//u@h:8080/p")) == "//u@h:8080/p"
normalize("HTTP://Example.COM:80/a/./b/../c") == "http://example.com/a/c"
resolve("http://a/b/c/d;p?q", "../g") == "http://a/b/g"
resolve("http://a/b/c/d;p?q", "?y") == "http://a/b/c/d;p?y"
```

Write a few quick checks of your own and run them with `python`, then reply "done".
