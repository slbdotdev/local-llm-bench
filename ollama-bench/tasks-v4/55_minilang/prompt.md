Create `minilang.py` in the current directory. It implements an interpreter for a small
expression language, standard library only. Write the lexer, parser and evaluator by hand:
do **not** use `eval`, `exec` or `compile`, and do **not** import `ast`, `operator` or
`functools`. Exact API:

- `MiniError` — an exception class you define. **Every** error, whether it happens while
  lexing, parsing or evaluating, is raised as a `MiniError` whose `.kind` attribute is one
  of exactly these strings: `"parse"`, `"dup_field"`, `"dup_binding"`, `"unbound"`,
  `"uninit"`, `"type"`, `"div_zero"`, `"no_field"`, `"no_match"`. Nothing else may be
  raised for bad input.
- `run(source)` — `source` is a string holding exactly one expression. Parses the whole
  source, then evaluates it, and returns the result converted to Python by rule 11.

## 1. Lexical structure

1. Whitespace (space, tab, CR, LF) separates tokens and is otherwise ignored. There are no
   comments.
2. An integer literal is either the single digit `0` or a digit `1`-`9` followed by any
   number of ASCII digits. There is no sign in a literal and no separators, and a **leading
   zero is rejected**: `0` and `40` are fine, `007` and `01` are `"parse"` errors. Only the
   ASCII digits `0`-`9` count as digits; any other Unicode digit character is a `"parse"`
   error.
3. String literals are `"` … `"`. The characters between the quotes may be anything except
   `"`, a backslash, or a newline; there are no escape sequences. `""` is the empty string.
4. Identifiers match `[A-Za-z_][A-Za-z0-9_]*`, ASCII only (a letter such as `é` is a
   `"parse"` error, not an identifier character). These 14 words are reserved and may never be
   used as an identifier (variable, parameter, field name or pattern variable):
   `let letrec and in if then else fun match with end ref true false`. The single
   underscore `_` is also reserved: it is the wildcard pattern and nothing else.
5. Operator/punctuation tokens, matched longest-first at each position:
   `-> := == != <= >= && || ++` then `+ - * / % < > = ( ) { } , . | !`. Any other character
   (for example `;`, `&`, `:`, `?`, `~`, `#`) is a lexical error.
6. Any lexical error is `MiniError` with kind `"parse"`.

## 2. Grammar

```
expr    := "let" IDENT "=" expr "in" expr
         | "letrec" IDENT "=" expr { "and" IDENT "=" expr } "in" expr
         | "if" expr "then" expr "else" expr
         | "fun" IDENT "->" expr
         | "match" expr "with" arm { arm } "end"
         | assign
arm     := "|" pattern "->" expr
assign  := orx [ ":=" expr ]
orx     := andx { "||" andx }
andx    := cmpx { "&&" cmpx }
cmpx    := catx [ ("=="|"!="|"<"|"<="|">"|">=") catx ]
catx    := addx [ "++" catx ]
addx    := mulx { ("+"|"-") mulx }
mulx    := unary { ("*"|"/"|"%") unary }
unary   := ("-" | "!" | "ref") unary | app
app     := postfix { postfix }
postfix := atom { "." IDENT }
atom    := INT | STRING | "true" | "false" | IDENT | "(" expr ")" | record
record  := "{" [ IDENT "=" expr { "," IDENT "=" expr } ] "}"
pattern := "_" | INT | STRING | "true" | "false" | IDENT
         | "{" [ IDENT "=" pattern { "," IDENT "=" pattern } ] "}"
```

`run` parses exactly one `expr` and then requires end of input; leftover tokens are a
`"parse"` error.

## 3. Precedence, loosest (1) to tightest (9)

| # | Forms | Associativity |
|---|---|---|
| 1 | `let`, `letrec`, `if`, `fun`, `match` | each subexpression extends as far to the right as possible, ending at the keyword the grammar demands (`in`, `then`, `else`, `with`, `end`), at `|`, at `)`, at `}`, at `,`, or at end of input |
| 2 | `:=` | right-associative: `a := b := c` is `a := (b := c)`. Its right side is a full `expr`, so `r := if c then 1 else 2` is legal, but its left side is not, so `let x = 1 in x := 2` parses as `let x = 1 in (x := 2)` |
| 3 | `\|\|` | left-associative, short-circuit |
| 4 | `&&` | left-associative, short-circuit |
| 5 | `== != < <= > >=` | **non-associative**: at most one of them may appear unparenthesised at this level, so `1 < 2 < 3` and `a == b == c` are `"parse"` errors |
| 6 | `++` (string concatenation) | **right-associative** |
| 7 | `+ -` | left-associative |
| 8 | `* / %` | left-associative |
| 9 | prefix `-` (negate), prefix `!` (dereference), prefix `ref` (allocate); then application by juxtaposition `f a`; then field access `e.f` | a prefix operator's operand is a `unary` (more prefixes, then an `app`), so `- - 1` is `1`; application is left-associative; field access binds tightest of all |

Consequences you must implement exactly:

1. `-x * y` is `(-x) * y`, and `- f x` is `-(f x)`, and `ref 1 + 2` is `(ref 1) + 2`,
   and `!r.f` is `!(r.f)`.
2. `f a b` is `(f a) b`; `f a.x` is `f (a.x)`; `f a + b` is `(f a) + b`;
   `f -1` is `f - 1` (subtraction), because `-` cannot start an argument.
3. An argument must be a `postfix` expression, so `f let x = 1 in x` and
   `f if c then a else b` are `"parse"` errors; write `f (let x = 1 in x)`.
4. `"a" ++ "b" ++ "c"` groups as `"a" ++ ("b" ++ "c")`.
5. `10 - 4 - 3` is `3`. `2 * 3 % 4` is `((2 * 3) % 4)`.

## 4. Values, and the order everything is evaluated in

The value kinds are **int**, **str**, **bool**, **record** (an unordered map from field
names to values), **closure**, and **ref** (a mutable cell).

6. **Default rule.** For every construct except the five listed in rule 7, all
   subexpressions are evaluated **left to right, completely, before any type is checked**.
   In particular, for a binary operator both operands are fully evaluated first; only then
   is the left operand's type checked, then the right operand's, and only after both types
   are accepted is a division-by-zero check performed. So `true + (1 / 0)` is `"div_zero"`,
   not `"type"`, and `"x" / 0` is `"type"`, not `"div_zero"`.
7. The five exceptions:
   - `if c then a else b`: evaluate `c`; if it is not a bool, `"type"`; then evaluate
     exactly one branch. The other branch is never evaluated.
   - `a && b`: evaluate `a`; if it is not a bool, `"type"` (**before `b` is evaluated at
     all**); if it is `false`, the result is `false` and `b` is never evaluated; otherwise
     evaluate `b`, and if `b` is not a bool, `"type"`; the result is `b`.
   - `a || b`: the mirror image — if `a` is `true`, the result is `true` and `b` is never
     evaluated.
   - `let x = e1 in e2`: `e1` is evaluated first, in the enclosing scope.
   - `match e with …`: `e` is evaluated first; matching a pattern never evaluates anything.
8. `run` parses the **entire** source before evaluating anything, so any parse-time error
   (kinds `"parse"`, `"dup_field"`, `"dup_binding"`) always wins over any runtime error.
   Parse-time errors are detected while parsing left to right, and the duplicate-name check
   for a construct happens at the moment that construct has been parsed through its closing
   token — so a violation inside a nested construct is reported before one in the construct
   that encloses it. Concretely: a record literal's or record pattern's duplicate-field check
   fires when its `}` is consumed; a match arm's repeated-variable check fires as soon as that
   arm's pattern has been parsed (before the arm's body); and a `letrec`'s duplicate-name
   check fires only once the whole `letrec`, body included, has been parsed.
9. Function application `f a`: evaluate `f`, then `a`, then require `f` to be a closure
   (else `"type"`), then evaluate the body with the parameter bound to `a`.
10. A record literal evaluates its field expressions in written order.

11. **Result conversion.** `run` returns: an int as a Python `int`, a bool as a Python
    `bool`, a str as a Python `str`, a record as a Python `dict` whose values are converted
    by this same rule, a closure as the string `"<fn>"`, and a ref as the string `"<ref>"`.

## 5. Scope

12. `let x = e1 in e2` binds `x` only inside `e2`; `x` is **not** in scope in `e1`.
    An inner binding shadows an outer one of the same name; the innermost wins.
13. `fun x -> e` builds a closure capturing the scope where it was written (lexical
    scoping). Later bindings never affect it.
14. `letrec x1 = e1 and … and xn = en in body` binds **all** of `x1…xn` in **all** of
    `e1…en` **and** in `body`. A right-hand side may be any expression, not only a `fun`.
    Every slot starts *uninitialised*; the right-hand sides are evaluated left to right and
    slot `xi` becomes initialised with the value of `ei` the moment `ei` finishes. Reading a
    name whose slot is still uninitialised raises kind `"uninit"`. (So
    `letrec a = 1 and b = a in b` is `1`, while `letrec a = b and b = 1 in a` is
    `"uninit"`.) Repeating a name in one `letrec` is kind `"dup_binding"`.
15. Reading a name that is bound nowhere is kind `"unbound"`.

## 6. Operators

16. `+ -` and `*` on two ints are the usual integer operations.
17. `/` is integer division that **truncates toward zero**: `7 / 2` is `3`, `-7 / 2` is
    `-3`, `7 / -2` is `-3`, `-7 / -2` is `3`.
18. `%` is the **floored** remainder: its result has the sign of the right operand (or is
    zero). `7 % 2` is `1`, `-7 % 2` is `1`, `7 % -2` is `-1`, `-7 % -2` is `-1`.
    Note that `/` and `%` deliberately do **not** agree: `a / b * b + a % b` need not be `a`.
19. `/` or `%` with a right operand of `0` is kind `"div_zero"` (after the type checks of
    rule 6).
20. `*` also does **string repetition** when the left operand is a str: then the right
    operand must be an int (else `"type"`), and the result is that many copies, with a
    count of `0` or less giving `""`. An int on the left and a str on the right is `"type"`.
21. `++` requires its **left** operand to be a str (else `"type"`). Its right operand may be
    a str (used as is), an int (rendered in decimal, negatives with a leading `-`), or a
    bool (rendered `true` / `false`); a record, closure or ref on the right is `"type"`.
    So `"n=" ++ 1 ++ "!"` is `"type"` (rule 4 of §3 groups it as `"n=" ++ (1 ++ "!")`).
22. `< <= > >=` require **two ints** (numeric order) or **two strings** (lexicographic by
    code point); anything else, including a mixed int/str pair, a bool, a record, a closure
    or a ref, is `"type"`.
23. `== !=` are allowed on two ints, two strings, two bools, or two refs (refs compare by
    identity: `true` only for the same cell). Any other combination — including int vs str
    and any record or closure operand — is `"type"`, **not** `false`.
24. Prefix `-` requires an int (else `"type"`). Prefix `!` requires a ref (else `"type"`)
    and yields the cell's current contents. `ref e` allocates a brand new cell holding `e`.
25. `a := b` evaluates `a`, then `b`, then requires `a` to be a ref (else `"type"`), stores
    `b` in that cell, and **returns `b`**.

## 7. Records and patterns

26. A record literal with a repeated field name is kind `"dup_field"`; so is a record
    *pattern* with a repeated field name. `{}` is the empty record.
27. `e.f` requires `e` to be a record (else `"type"`); if the record has no field `f` the
    kind is `"no_field"`.
28. `match` tries the arms **in written order and takes the first one whose pattern
    matches**; if none matches, kind `"no_match"`.
29. Pattern matching: `_` matches anything and binds nothing. An identifier matches anything
    and binds it. An int / string / `true` / `false` pattern matches only a value of that
    same kind that is equal to it (a str pattern never matches an int, and so on). A record
    pattern `{f1 = p1, …}` matches a **record** that has at least the listed fields (extra
    fields are allowed and ignored) and whose corresponding values all match; the fields are
    tested in written order. Against a non-record it simply fails to match — it is not an
    error.
30. All the variables of one pattern must be distinct; repeating a variable inside a single
    pattern is kind `"dup_binding"` (two different arms may of course use the same name).
    A pattern's variables are in scope only in that arm's body, shadowing outer bindings.

## 8. Strictness requirements (all of these are tested)

31. Every rejection listed anywhere above must raise **your** `MiniError` with the right
    `.kind`. A `ZeroDivisionError`, `KeyError`, `TypeError`, `RecursionError`,
    `AttributeError`, bare `Exception`, or any other class is wrong, and so is silently
    returning something instead of raising. `MiniError` must be a subclass of `Exception`.
32. `.kind` must be exactly one of the nine strings listed at the top; no other value,
    and no missing attribute.
33. The returned Python types must be exact: a bool result is `True`/`False` (not `1`/`0`),
    an int result is an `int` (not a `bool` and not a string), a record is a `dict` (not a
    list of pairs), and a closure/ref is exactly the string `"<fn>"` / `"<ref>"`.
34. Integer literals with a leading zero, non-ASCII characters, a bare `_` used as an
    expression or as a binder, and a reserved word used as an identifier, parameter or
    field name (e.g. `{end = 1}`, `fun in -> 1`) are all `"parse"` errors.
35. A source that is empty or only whitespace is a `"parse"` error.
36. `/` and `%` must follow rules 17 and 18 exactly for negative operands; do not use
    Python's `//` for `/`, and do not use C's `%` for `%`.
37. The evaluation orders of rules 6, 7, 8 and 9 must be followed exactly, since they decide
    *which* error is reported when several are possible.
38. Do not use `eval`, `exec` or `compile`, and do not import `ast`, `operator` or
    `functools`.

## Examples

```python
run("1 + 2 * 3")                                              # 7
run("let x = 4 in x * x")                                     # 16
run("letrec f = fun n -> if n == 0 then 1 else n * f (n - 1) in f 5")   # 120
run('match {tag = "pt", x = 3} with | {tag = "pt", x = v} -> v + 1 | _ -> 0 end')  # 4
run("let r = ref 2 in r := !r + 3")                           # 5
run("{a = 1}.b")                                              # raises MiniError, .kind == "no_field"
```

Write a few quick checks of your own and run them with `python`, then reply "done".
