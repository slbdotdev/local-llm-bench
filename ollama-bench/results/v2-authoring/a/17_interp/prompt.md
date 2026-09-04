Create `interp.py` in the current directory with a function

    evaluate(source: str)

that parses and evaluates one expression of a tiny expression language and returns the resulting value as a Python value:

- an integer result is returned as a Python `int`,
- a string result as a Python `str`,
- a comparison result as a Python `bool`,
- a function (closure) result as a Python callable `f(arg)` taking exactly one argument; calling it evaluates the function body with the argument bound (errors raised during that call are also `InterpError`).

## Lexical structure
- Integer literals: one or more digits, e.g. `0`, `42`. No sign, no separators.
- String literals: a double quote, then zero or more characters, then a double quote. The enclosed characters may not include `"`, a backslash, or a newline. There are no escape sequences. Examples: `""`, `"hello"`.
- Identifiers: `[A-Za-z_][A-Za-z0-9_]*`. The keywords `let`, `in`, `if`, `then`, `else`, `fn` are reserved and may not be used as identifiers.
- Operator and punctuation tokens: `+ - * / == != < <= > >= ( ) = ->`. A lone `!`, `&`, `|`, `,`, `'`, `'` etc. is a parse error.
- Whitespace separates tokens and may appear anywhere between tokens.

## Grammar (exactly one expression per `evaluate` call)

```
expr     := ifexpr | letexpr | fnexpr | cmpexpr
ifexpr   := "if" expr "then" expr "else" expr
letexpr  := "let" IDENT "=" expr "in" expr
fnexpr   := "fn" IDENT "->" expr
cmpexpr  := addexpr ( ("=="|"!="|"<"|"<="|">"|">=") addexpr )?
addexpr  := mulexpr ( ("+"|"-") mulexpr )*
mulexpr  := appexpr ( ("*"|"/") appexpr )*
appexpr  := atom { atom }
atom     := INT | STRING | IDENT | "(" expr ")"
```

After parsing one `expr`, any leftover input is a parse error.

## Precedence, from loosest to tightest

| Level | Form | Associativity |
|---|---|---|
| 1 (loosest) | `if c then a else b`, `let x = e1 in e2`, `fn x -> e` | the condition/branches/RHS/body each extend as far right as possible; they end at a closing paren, at the next relevant keyword (`then`, `else`, `in`), or at end of input |
| 2 | comparisons `== != < <= > >=` | **non-associative**: at most one comparison operator may appear at this level unparenthesised; `1 < 2 < 3` is a parse error |
| 3 | additive `+ -` | left-associative |
| 4 | multiplicative `* /` | left-associative, binds tighter than additive: `1 + 2 * 3` is `7` |
| 5 (tightest) | function application by juxtaposition `f x` | left-associative, binds tighter than every operator: `f 1 + 2` is `f(1) + 2`, `f 1 2` is `(f(1))(2)`, `let f = fn x -> x in f 1 == 1` is `True` |

Notes:
- There is **no unary minus**: `-` exists only as a binary operator, so a leading `-` is a parse error. Negative values are written e.g. `0 - 7`.
- In an application `f x`, the argument must be a bare atom (literal, identifier, or parenthesised expression). Anything else — `f x * y`, `f if ...`, `f let ...`, `f fn ...` — must be parenthesised to be an argument.
- Examples: `10 - 4 - 3` is `3`; `10 - (4 - 3)` is `9`; `0 - 7 / 2` is `-3`; `(0 - 7) / 2` is `-3`.

## Semantics
- `let x = e1 in e2`: evaluate `e1` in the current scope, bind `x` to it in a *new* scope extending the current one, evaluate `e2` in that new scope. Shadowing is allowed; the innermost binding wins. Example: `let x = 1 in let x = x + 2 in x * 10` evaluates to `30`. The name is *not* in scope inside its own right-hand side.
- `fn x -> e`: creates a closure that captures the bindings visible where it is created (lexical scoping). Bindings created later must not affect it: `let y = 10 in let f = fn x -> x + y in let y = 99 in f 1` evaluates to `11`.
- Application `f a`: evaluate `f` and `a`; `f` must be a closure, otherwise runtime error.
- `if c then a else b`: `c` must evaluate to a boolean (i.e. the result of a comparison); only the taken branch is evaluated.
- Arithmetic `+ - * /`: both operands must be integers; booleans are not integers here. `/` is integer division that truncates toward zero: `7 / 2` is `3`, `(0 - 7) / 2` is `-3`.
- Comparisons: `==` and `!=` require both operands to be of the same type — both integers or both strings; comparing an integer with a string, comparing booleans, or comparing functions is a type mismatch. `<`, `<=`, `>`, `>=` require both operands to be integers.
- Booleans are real values: a comparison may be let-bound, returned from a closure, or passed around, but any use of a boolean other than as an `if` condition (arithmetic, comparison, application) is a type mismatch.

## Errors
Every error — parse error or runtime error — must raise the single exception class `InterpError(Exception)` defined in `interp.py`. Nothing else may be raised for bad input. Runtime errors include:

- unbound identifier (e.g. `x`, or `let x = 1 in y`),
- type mismatch (arithmetic on non-integers, `"a" + 1`, `"a" < "b"`, `1 == "a"`, `if 1 then ... else ...`, `(1 < 2) + 3`, `(1 < 2) == (2 < 3)`, applying a closure to a string when it expects to add integers, etc.),
- division by zero (`1 / 0`, `1 / (2 - 2)`),
- applying a non-function (`5 3`, `"f" 1`, `let f = 1 in f 2`).

Parse errors include: empty input, unbalanced parentheses, unterminated string literal, dangling or doubled operators (`1 +`, `1 + * 2`), missing `then`/`else`/`in`/`->`, chained comparisons (`1 < 2 < 3`), a reserved keyword used as an identifier (`let if = 1 in 1`), an atom expected but not found, unexpected trailing input.

Write a few quick checks of your own and run them with `python`, then reply "done".