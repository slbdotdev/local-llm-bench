Create `minilang.py` in the current directory: a small interpreter for a toy language. Standard library only.

Public API:

```python
run(src: str) -> list[str]        # execute a program, return the lines it printed
evaluate(src: str) -> object      # evaluate ONE expression (no trailing ';'), return its value
```

plus these exception classes:

```python
class LangError(Exception): ...           # base, has .kind and .line
class LexError(LangError): ...            # .kind == "lex"
class ParseError(LangError): ...          # .kind == "parse"
class UndefinedNameError(LangError): ...  # .kind == "name"
class TypeMismatchError(LangError): ...   # .kind == "type"
class DivideByZeroError(LangError): ...   # .kind == "zero"
```

Every error raised by `run`/`evaluate` for bad input must be one of the five subclasses. `.line` is the 1-based source line of the offending token, `.kind` is the string above, and

```
str(e) == "<kind> error at line <line>: <detail>"
```

The `<detail>` text is specified exactly for lex and name errors (below); for parse, type and zero errors the detail is up to you (it must be non-empty).

## 1. Lexing

Tokens: numbers, strings, names, keywords, and the operators/punctuation
`** == != <= >= < > = + - * / % ( ) { } ;`.

- Whitespace (space, tab, CR, LF) separates tokens and is otherwise ignored.
- `#` starts a comment that runs to the end of the line (or end of source).
- Number literals are `digits` (an int) or `digits.digits` (a float). Both sides of the `.` are required.
- A number literal is scanned greedily as a digit followed by any run of digits, letters, `_` and `.`; if that run is not exactly `digits` or `digits.digits` it is a lex error with detail `malformed number '<text>'` (so `1.`, `1.2.3`, `12abc`, `1e5` all fail). There is no exponent notation.
- String literals are double-quoted. The only valid escapes are `\n`, `\t`, `\\` and `\"`. Any other backslash escape is a lex error with detail `invalid escape '\<c>'` (e.g. `invalid escape '\q'`). A string that hits a newline or the end of the source before its closing quote is a lex error with detail `unterminated string`; its `.line` is the line the string STARTED on.
- Names match `[A-Za-z_][A-Za-z_0-9]*`. These are keywords and may not be used as variable names: `let print if else while and or not true false`.
- Any other character is a lex error with detail `unexpected character '<c>'` (e.g. `unexpected character '@'`).

## 2. Grammar

```
program  := stmt*
stmt     := "let" NAME "=" expr ";"
          | NAME "=" expr ";"
          | "print" expr ";"
          | "{" stmt* "}"
          | "if" "(" expr ")" stmt [ "else" stmt ]
          | "while" "(" expr ")" stmt

expr     := or_expr
or_expr  := and_expr ("or" and_expr)*
and_expr := not_expr ("and" not_expr)*
not_expr := "not" not_expr | cmp
cmp      := add [ ("==" | "!=" | "<" | "<=" | ">" | ">=") add ]
add      := mul (("+" | "-") mul)*
mul      := unary (("*" | "/" | "%") unary)*
unary    := ("-" | "+") unary | power
power    := primary ["**" unary]
primary  := NUMBER | STRING | "true" | "false" | NAME | "(" expr ")"
```

Consequences you must get right:

- `+ -` are left-associative; so are `* / %`.
- `**` is RIGHT-associative and binds tighter than unary minus on its left, but its right operand is a full `unary`. So `2 ** 3 ** 2` is `2 ** (3 ** 2)` = 512, `-2 ** 2` is `-(2 ** 2)` = -4, `(-2) ** 2` is 4, `2 ** -1` is legal and is 0.5, and `-2 ** -2` is -0.25.
- Comparison is NON-associative: exactly zero or one comparison operator per `cmp`. `1 < 2 < 3` is a parse error. Use parentheses if you mean something.
- `not` binds looser than comparison but tighter than `and`: `not 1 == 2` is `not (1 == 2)`, and `not true or true` is `(not true) or true`.
- `and` binds tighter than `or`: `true or false and false` is `true or (false and false)`.
- `else` binds to the nearest unmatched `if`.
- A `{ ... }` block may be empty. An empty program is legal and prints nothing.

Anything the grammar does not accept is a `ParseError` at the line of the first offending token (`unexpected end of input` when the source runs out).

## 3. Values, types and operators

There are exactly four value types: **int**, **float**, **bool**, **string**. Booleans are NOT numbers: `true + 1` is a type error, and `true == 1` is `false`.

- `+` : number+number (numeric addition) or string+string (concatenation). Anything else is a type error.
- `-` `*` : numbers only.
- `/` : numbers only; the result is ALWAYS a float (`4 / 2` is `2.0`). A zero divisor (int `0` or float `0.0`) is a zero error.
- `%` : numbers only; same sign convention as Python (`-7 % 3` is `2`). A zero right operand is a zero error.
- `**` : numbers only. `int ** non-negative-int` is an int; every other combination is a float (so `2 ** 3` is `8`, `2 ** -1` is `0.5`, `2.0 ** 2` is `4.0`). If the base is zero and the exponent is negative, that is a zero error.
- unary `-` / `+` : numbers only (`-true` and `-"x"` are type errors).
- `==` and `!=` : accept ANY two values and never raise. Two numbers compare by numeric value (`1 == 1.0` is `true`). Otherwise values of different types are never equal (`1 == "1"` is `false`, `true == 1` is `false`, `1 == 1.0` is `true` because both are numbers). Same-type values compare normally.
- `< <= > >=` : number vs number, or string vs string (lexicographic by Unicode code point). Any other combination is a type error.
- `not X` always yields a bool.
- `and` / `or` short-circuit and return an OPERAND, not a bool (Python-style): `A and B` evaluates `A`; if `A` is falsy the result is `A` and `B` is NEVER evaluated; otherwise the result is `B`. `A or B` evaluates `A`; if `A` is truthy the result is `A` and `B` is NEVER evaluated; otherwise the result is `B`. So `1 and 2` is `2`, `0 or "z"` is `"z"`, `"" or 0` is `0`.
- Falsy values are exactly `false`, `0`, `0.0` and `""`. Everything else is truthy. `if` and `while` use the same rule.

## 4. Statements and scoping

- The program runs in a global scope. Each `{ ... }` block creates a new scope that disappears when the block ends. `if`/`while` bodies that are not blocks do NOT create a scope.
- `let x = e;` evaluates `e` FIRST and then declares `x` in the current scope. So `let x = x + 1;` inside a block reads the OUTER `x`.
- Declaring a name that is already declared in the SAME scope is a name error with detail `duplicate declaration '<name>'`, at the line of the `let` keyword. Declaring it in an inner scope (shadowing) is fine.
- `x = e;` assigns to the nearest enclosing scope that declares `x`; it never creates a variable. If no scope declares `x` it is a name error with detail `undefined variable '<name>'`, at the line of the name token.
- Reading an undeclared name is a name error with the same detail, at the line of the name token.
- `print e;` appends one rendered line to the output list.

Rendering (`print`, and only `print`, uses this):
- bool -> `true` or `false`
- int -> its decimal digits, e.g. `-4`
- float -> exactly Python's `repr()` of the float, e.g. `2.0`, `0.5`, `-0.25` (infinities and NaN will not be tested)
- string -> its characters verbatim, with no quotes and no escaping

If a program raises, `run` propagates the error and the output collected so far is discarded.

## 5. Error precedence

1. The WHOLE source is lexed before anything is parsed. If it contains any lex error, the earliest one (by position) is raised, even if there is also a parse error earlier in the file.
2. The WHOLE program is parsed before anything is executed. If it contains any parse error, the earliest one is raised and NOTHING is executed (no output).
3. Runtime errors then surface in strict left-to-right, top-to-bottom evaluation order. A binary operator evaluates its left operand fully, then its right operand, and only then checks types. So `zzz + (1 / 0)` is a name error while `(1 / 0) + zzz` is a zero error.
4. An error inside an operand that `and`/`or` skipped never happens: `false and zzz` is `false`, `true or (1 / 0)` is `true`.

## 6. Performance

`run` must be roughly linear in the size of the source and in the number of operations executed. On a normal laptop:

- a program of 40,000 statements (about 760 KB of source) must lex, parse and run in under 6 seconds;
- a `while` loop of 200,000 iterations with a small body must run in under 6 seconds.

Do not re-slice the source string per token, do not re-parse or re-tokenize anything per loop iteration, and do not copy the whole variable environment per statement. Expression and block nesting in the tested programs never exceeds depth 50, so ordinary recursive descent and a recursive evaluator are safe.

## 7. Worked examples

```python
run("print 1 + 2 * 3;\nprint -2 ** 2;\nprint 2 ** -1;\nprint 2 ** 3 ** 2;")
# -> ["7", "-4", "0.5", "512"]

run('let x = 1;\n{ let x = x + 10; print x; }\nprint x;\n{ x = 99; }\nprint x;')
# -> ["11", "1", "99"]

run('let i = 0;\nwhile (i < 3) { print i * 2; i = i + 1; }  # a comment\nprint "done";')
# -> ["0", "2", "4", "done"]

evaluate("1 and 2")          # -> 2
evaluate('"" or 0')          # -> 0
evaluate("not 1 == 2")       # -> True
evaluate("4 / 2")            # -> 2.0
evaluate("true == 1")        # -> False

try:
    run("print 1;\nprint zzz;")
except UndefinedNameError as e:
    str(e)   # "name error at line 2: undefined variable 'zzz'"
    e.kind   # "name"
    e.line   # 2
```

Write a few quick checks of your own and run them with `python`, then reply "done".
