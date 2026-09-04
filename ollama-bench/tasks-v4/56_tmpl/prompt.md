Create `tmpl.py` in the current directory. It implements a small text template engine as
pure string processing, and must define exactly this API:

- `TemplateError` — an exception class you define. Every instance has two attributes:
  `.kind`, one of the fixed strings `"unclosed_tag"`, `"unknown_tag"`, `"unexpected_tag"`,
  `"unclosed_block"`, `"syntax"`, `"unknown_filter"`, `"filter_args"`, `"bad_operand"`,
  `"not_iterable"`; and `.pos`, an `int` giving the **0-based character offset, in the
  original template source, of the `{` that opens the tag the error is attributed to**
  (for `unclosed_block` that is the `{` of the block-opening tag that was never closed).
- `render(source, context)` -> `str`. `source` is the template text; `context` is a `dict`
  mapping names to values. Values are built only from `dict` (string keys), `list`, `str`,
  `int`, `bool` and `None`. Returns the rendered text, or raises `TemplateError`.

**Bans.** You may not import `re`, `string` (or use `string.Template`), `html` (or
`html.escape`), or `shlex`, you may not use any third-party templating library, and you may
not call `eval()` or `exec()`. Write everything by hand.

**Strictness.** These are graded separately from ordinary rendering, and each one is easy
to get wrong without noticing:

1. Every rejected template raises **your** `TemplateError` — never `ValueError`, `KeyError`,
   `IndexError`, `AttributeError`, `RecursionError` or anything else — and never silently
   renders the offending tag as literal text.
2. `.kind` is exactly one of the nine strings above and `.pos` is exactly the offset
   defined above; both are checked.
3. The phase order (lex, then parse, then render) and the leftmost-first rule decide which
   error is raised when a template breaks several rules at once.
4. The escape replacements are performed in one pass so that `&` produced by an earlier
   replacement is never re-escaped, and only the five listed characters are touched.
5. Whitespace-control trimming is unbounded and crosses newlines, and never reaches past a
   tag.
6. `safe` is sticky through every later filter.
7. The truthiness rule in 3.3 is deliberately not Python's.
8. `render` always returns a `str`; `loop.first` / `loop.last` are real booleans (so
   `loop.first == 1` is false); no extra or missing whitespace is ever introduced.

Processing happens in three phases, in this order: **lexing**, then **parsing**, then
**rendering**. All of lexing finishes before any parsing; all of parsing finishes before
any rendering. This fixes which error wins when several are possible.

## 1. Lexing

Scan `source` left to right. At each position, if the current character is `{` and the next
character is `{`, `%` or `#`, a tag starts here; otherwise the character is literal text.
There is no escape sequence for `{`. The three tag kinds and their closers are:

| opener | closer | kind |
|---|---|---|
| `{{` | `}}` | interpolation |
| `{%` | `%}` | block tag |
| `{#` | `#}` | comment |

1. A tag runs from its opener up to and including the **first** occurrence of its own
   closer, searching from just after the opener (and after the optional `-` of rule 3).
   The lexer knows nothing about quotes or nesting: `{% if x == "%}" %}` ends at the first
   `%}`, so its body is `if x == "`; `{# a {# b #} c #}` ends at the first `#}`, leaving
   ` c #}` as literal text. Comments do **not** nest.
2. If a tag's closer never occurs, raise `unclosed_tag` at the offset of that tag's `{`.
   Lexing scans left to right, so this is the leftmost such tag.
3. **Whitespace control.** A `-` immediately after the opener is a *left marker*; a `-`
   immediately before the closer is a *right marker*. Both are stripped and are not part of
   the tag body. They are available on all three tag kinds (`{{- -}}`, `{%- -%}`,
   `{#- -#}`). Only these six characters count as whitespace anywhere in this spec:
   space, tab, carriage return, newline, vertical tab (U+000B), form feed (U+000C).
4. Lexing produces an alternating sequence of literal-text runs and tags. Trimming is then
   applied to the literal-text runs, computed from the **original** runs:
   a. If the tag immediately before a text run has a *right* marker, remove every leading
      whitespace character of that run.
   b. If the tag immediately after a text run has a *left* marker, remove every trailing
      whitespace character of that run.
   Trimming is unbounded and crosses newlines: it removes the whole whitespace run, however
   many newlines it contains. Both (a) and (b) may apply to the same run; if the run is
   entirely whitespace it then becomes empty, which is not an error. Trimming never removes
   anything but literal text: if there is no text run between two tags, a marker has no
   effect, and a marker never reaches past a tag into an earlier or later text run. A left
   marker on the first tag of the template, or a right marker on the last, with no text run
   on that side, does nothing. Trimming happens once, at lex time; a tag inside a loop body
   therefore trims the same source text no matter how many times the loop runs.
5. Comment tags are then discarded entirely (their trimming from rule 4 still applies).

## 2. Parsing

A tag body is stripped of leading and trailing whitespace before it is examined.

- An interpolation with an empty body is `syntax`.
- A block tag whose body is empty is `unknown_tag`. Otherwise its **name** is the leading
  run of non-whitespace characters, and the **rest** is what follows, stripped. The names
  are `if`, `elif`, `else`, `endif`, `for`, `empty`, `endfor`, `set`; any other name is
  `unknown_tag`.
- `else`, `endif`, `empty`, `endfor` must have an empty rest, else `syntax`.
  `if` and `elif` must have a non-empty rest (the condition), else `syntax`. For all six of
  these the structural check below happens **first**: `{% else x %}` at top level is
  `unexpected_tag`, while `{% if 1 %}{% else x %}{% endif %}` is `syntax`.

Block structure:

- `{% if C %} body ({% elif C %} body)* ({% else %} body)? {% endif %}`, nestable.
- `{% for NAME in EXPR %} body ({% empty %} body)? {% endfor %}`, nestable.
- `{% set NAME = EXPR %}` — the rest must be an identifier, optional whitespace, a single
  `=` that is not the start of `==`, then a non-empty expression; otherwise `syntax`.

A closing/continuation tag that does not fit the innermost open block is `unexpected_tag`
at its own offset — this covers `endif`/`endfor`/`else`/`elif`/`empty` at top level, an
`elif` or `else` after an `else`, a second `empty`, an `else` inside a `for` body, an
`endfor` closing an `if`, and so on. If the end of the template is reached with blocks
still open, raise `unclosed_block` at the offset of the **innermost** (most recently
opened) unclosed block. Otherwise parse errors are reported for the leftmost offending
tag, since tags are parsed left to right; within a single tag, the errors are checked in
the order they are described here.

### 2.1 Expressions

Whitespace between tokens in an expression is insignificant. The grammar, loosest binding
first:

```
pipeline   := disjunct ( "|" filter )*
disjunct   := conjunct ( "or" conjunct )*
conjunct   := negation ( "and" negation )*
negation   := "not" negation | comparison
comparison := primary [ cmpop primary ]
cmpop      := "==" | "!=" | "<" | "<=" | ">" | ">=" | "in"
primary    := atom ( "." key | "[" primary "]" )*
atom       := INT | STRING | "true" | "false" | "none" | IDENT
```

- `not` binds **looser** than a comparison, so `not a == b` means `not (a == b)`.
- Comparison is non-associative: a second `cmpop` in a row (`a < b < c`) is `syntax`.
- The filter pipeline applies to the **whole** expression, so `{{ a or b | upper }}` means
  `(a or b) | upper`.
- A filter pipeline is allowed only in `{{ }}`, in `{% set %}` and in the `EXPR` of a
  `for` tag. A `|` in an `if`/`elif` condition is `syntax`.
- `INT` is one or more ASCII digits (no sign, no decimal point). `IDENT` is a letter or `_`
  followed by letters, digits and `_`; the eight words `true`, `false`, `none`, `not`,
  `and`, `or`, `in` are keywords and are never identifiers (but they *are* legal as a `key`
  after a `.`). Anything the grammar cannot consume, and any leftover text at the end of an
  expression, is `syntax`.
- `STRING` is delimited by `'` or `"`. Inside it, `\n` means newline, `\t` means tab, and
  `\` followed by any other character (including `\`, `'` and `"`) means that character
  itself. An unterminated string is `syntax`.
- `key` after a `.` is an identifier (used as-is, as a string) or a run of ASCII digits
  (also used as a string, so `a.0` looks up the key `"0"`). Inside `[ ]` the subscript is a
  `primary`, so `a["k"]`, `a[0]` (an **integer**, not the string `"0"`) and `a[i.j]` are
  all allowed. A missing `]` is `syntax`.

### 2.2 Filters

After the `|`, skip whitespace and read the filter name (letters, digits, `_`; it may not
start with a digit). An empty name is `syntax`. A name not in the table below is
`unknown_filter`. Then, skipping whitespace, if the next character is `:` an argument list
follows. Then, skipping whitespace, the next character must be `|` (another filter) or the
end of the expression; anything else is `syntax`. Finally, if the number of arguments does
not equal the filter's declared arity, that is `filter_args`. (So for one filter the checks
run in the order: unknown name, then argument syntax, then arity.)

An argument list is one or more arguments separated by `,`. Each argument is read like
this, after skipping leading whitespace:

- If the next character is `'` or `"`, read a `STRING` as in 2.1. Then skip whitespace; the
  next character must be `,`, `|`, or the end of the expression, else `syntax`.
- Otherwise the argument is the **maximal run of characters up to (but not including) the
  next `,` or `|` or the end of the expression**, with leading and trailing whitespace
  removed. Quote characters inside such a run are ordinary characters. The resulting text
  is then interpreted: one or more ASCII digits means that integer; exactly `true`,
  `false` or `none` means that value; anything else — including the empty string — means
  that text as a string. **A bare argument is never a variable lookup**: `default:x` means
  the string `"x"`, and `replace:a b, ` means the strings `"a b"` and `""`.

So `:` introduces at least one argument: `default:` has one argument, the empty string.

| filter | arity | meaning |
|---|---|---|
| `upper` | 0 | the value's **text** (see 3.1) with ASCII `a`-`z` mapped to `A`-`Z` |
| `lower` | 0 | the value's text with ASCII `A`-`Z` mapped to `a`-`z` |
| `trim` | 0 | the value's text with whitespace stripped from both ends |
| `length` | 0 | integer: `0` for undefined, `none` and booleans; the number of digits of the decimal text of an integer; otherwise the number of characters / items / keys |
| `first` | 0 | first character of a string, first item of a list, first key of a map, else undefined; undefined if empty |
| `safe` | 0 | the value unchanged, marked safe |
| `escape` | 0 | the value's text, HTML-escaped as in 3.2, marked safe |
| `default:X` | 1 | `X` if the value is **falsy** (3.3), otherwise the value unchanged |
| `join:S` | 1 | list: items' texts joined by the text of `S`; string: its characters joined by it; map: its keys joined by it; undefined/`none`: `""`; number/boolean: its own text |
| `replace:A,B` | 2 | the value's text with non-overlapping left-to-right occurrences of the text of `A` replaced by the text of `B`; if `A` is `""` the text is returned unchanged |
| `slice:START,LEN` | 2 | if `START` or `LEN` is not an integer >= 0 nor a run of ASCII digits, the value is returned unchanged; otherwise the `LEN` items/characters starting at index `START` of the value if it is a list or a string, or of its text if it is not. Out-of-range indices clamp: the result is simply as long as the available material allows, and is never an error |

Filters never raise. `upper`, `lower`, `trim`, `replace` and `join` always produce a
string; `slice` of a list produces a list.

## 3. Rendering

The output is the concatenation, in source order, of the literal-text runs (never escaped,
never altered beyond rule 4 trimming) and of the rendered tags.

### 3.1 Values and text

The value types are **undefined** (the result of every failed lookup), `none`, boolean,
number, string, list and map. Their `type` names are, respectively: undefined has none,
then `"none"`, `"bool"`, `"number"`, `"string"`, `"list"`, `"map"`. Booleans are *not*
numbers.

The **text** of a value:

- undefined and `none` -> `""`
- `true` -> `"true"`, `false` -> `"false"`
- number -> its decimal digits (with a leading `-` if negative)
- string -> itself
- list -> `[`, the texts of the items separated by `, `, `]` — e.g. `[a, 2, true]`
- map -> `{`, then for each key in insertion order the key's text, `: `, the value's text,
  separated by `, `, then `}` — e.g. `{a: 1, b: x}`

### 3.2 Auto-escaping

Every value produced by a `{{ }}` is converted to its text, and then, **unless the value is
marked safe**, each of these five characters is replaced, in a single left-to-right pass
(replacements are never rescanned):

`&` -> `&amp;` , `<` -> `&lt;` , `>` -> `&gt;` , `"` -> `&#34;` , `'` -> `&#39;`

Nothing else is ever escaped: literal template text is not escaped, string literals used as
filter arguments are not escaped, and values used in conditions, in `for` and in `set` are
not escaped.

Safety is **sticky**: `safe` and `escape` mark the value safe, and *every* filter applied
afterwards preserves that mark, even filters that change the text. So
`{{ x | escape | upper }}` with `x = "a&b"` renders `A&AMP;B`. The one exception is
`default` when it actually substitutes: the substituted argument is never safe. A value
stored by `{% set %}` keeps its mark, and reading it back as a **bare name** in a `{{ }}`
gets it back; any other use of it — `.` or `[]` lookup on it, comparison, `and`/`or`/`not`
— produces an unmarked value.

### 3.3 Truthiness

Exactly these values are **falsy**: undefined, `none`, `false`, the number `0`, the empty
string, the string `"0"`, the string `"false"`, the empty list, the empty map. Everything
else is truthy — including the string `" "`, the string `"False"`, the string `"0.0"` and
the number `-1`.

### 3.4 Lookup

`base . key` and `base [ key ]` both resolve as follows, given the value of `base` and the
key (a string, an integer, or any other value from a subscript):

1. If `base` is undefined or `none`, the result is undefined.
2. If `base` is a map and the key is present in it (compared exactly, so the integer `0`
   never matches the key `"0"`), the result is that entry.
3. Otherwise, if `base` is a list or a string and the key is an integer (booleans do not
   count) or a non-empty run of ASCII digits, that index is used: if it is within
   `0 <= i < length` the result is the item (a one-character string for a string), and
   otherwise the result is undefined. Negative indices are never valid.
4. Otherwise three built-in pseudo-keys are tried, which are therefore *shadowed* by a real
   map key of the same name: `size` is the number of characters / items / keys of a string,
   list or map (undefined for other types); `keys` is the list of a map's keys in insertion
   order (undefined for other types); `type` is the type name from 3.1 (undefined for
   undefined, and note that step 1 means `x.type` is undefined, not `"none"`, when `x` is
   `none`).
5. Otherwise the result is undefined.

A failed lookup is never an error; undefined renders as the empty string.

### 3.5 Conditions

`and` and `or` short-circuit: as soon as the result is determined the remaining operands
are **not evaluated**, so an error they would raise does not happen. `not`, `and` and `or`
yield the booleans `true`/`false`, never an operand.

- `==` / `!=` compare by type first: values of different types are never equal, so
  `1 == true`, `"1" == 1` and `none == x` (`x` undefined) are all false. Two undefined
  values are equal, and two `none` values are equal. Lists are equal if they have the same
  length and equal items in order; maps are equal if they have the same number of keys and
  each key of one is present in the other with an equal value (key order is irrelevant).
- `<`, `<=`, `>`, `>=` require **both** operands to be numbers, or **both** to be strings
  (compared by code point, character by character). Anything else — including a boolean, a
  number against a string, or anything undefined — raises `bad_operand` at the offset of
  the enclosing tag.
- `x in y`: if `y` is a string, the result is `true` iff `x` is a string and a substring of
  `y` (`"" in "ab"` is true); if `y` is a list, iff some item equals `x` by the `==` rule;
  if `y` is a map, iff `x` is a string and a key of `y`. For any other `y` the result is
  `false` — never an error.

### 3.6 `for`

The `EXPR` is evaluated, and its **sequence** is: a list -> its items; a string -> its
characters; a map -> its keys; undefined or `none` -> the empty sequence. A number or a
boolean raises `not_iterable` at the offset of the `for` tag.

If the sequence is empty, the `{% empty %}` body is rendered (nothing, if there is none)
and the loop body is not rendered at all.

The `for` tag pushes exactly one new scope, which is discarded at `{% endfor %}`. Both the
loop body and the `empty` body are rendered inside that scope. Each iteration rebinds, in
that scope, `NAME` to the current item and `loop` to a map with exactly these five keys, in
this order:

`index` (1-based), `index0` (0-based), `first`, `last`, `length` (the number of items)

`NAME` and `loop` shadow anything of the same name from an enclosing scope for the duration
of the loop, and both revert to their previous values (possibly undefined) at `endfor`.
Inside a nested loop, `loop` refers to the **innermost** enclosing loop only; there is no
way to reach an outer loop's `loop` (in particular `loop.parent` is just a failed lookup,
i.e. undefined). Inside the `empty` body, `loop` is whatever it was outside the loop.

### 3.7 `set`

`{% set NAME = EXPR %}` evaluates `EXPR` (safety mark included) and binds `NAME` in the
**innermost scope that currently exists**. `if`/`elif`/`else` bodies do **not** create a
scope, so a `set` inside them leaks out to the enclosing scope. A `for` pushes a scope, so
a `set` anywhere inside a loop body binds in the loop's scope: it survives from one
iteration to the next, and it is gone after `endfor`. A `set` whose tag is never reached
(a branch not taken, a loop that never runs) binds nothing.

Examples:

- `render("Hello {{ name | upper }}!", {"name": "ada"})` == `"Hello ADA!"`
- `render("{% for c in cs %}{{ loop.index }}.{{ c }} {% empty %}none{% endfor %}", {"cs": ["a", "b"]})` == `"1.a 2.b "`
- `render("{{ bio }}", {"bio": "<b>x</b>"})` == `"&lt;b&gt;x&lt;/b&gt;"`
- `render("A\n  {%- if ok %}yes{% endif %}", {"ok": True})` == `"Ayes"`
- `render("{{ miss | default:'n/a' }}", {})` == `"n/a"`

Write a few quick checks of your own and run them with `python`, then reply "done".
