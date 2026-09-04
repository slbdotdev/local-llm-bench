The current directory contains a tiny text template engine split over two modules —
`tlex.py` (tokenizer) and `trender.py` (parser + renderer) — plus `test_tmpl.py`, a
small visible test file. The implementation has several behavioural bugs, in **both**
files. Fix them so the engine matches the specification below exactly.

Deliverable: the same two modules, `tlex.py` and `trender.py`, still split the same
way (`trender` imports `tlex`). Do NOT edit `test_tmpl.py`. The graded entry points are
`trender.render(text, ctx)` and `trender.TemplateError`; the token representation used
between the two modules is yours to keep or change. Define `TemplateError` in `tlex.py`
and import it into `trender.py` so that `trender.TemplateError` names that same class.

`render(text, ctx)` takes template text and a context dict and returns a string.
`ctx` values are only ever `str`, `int`, `bool`, `list`, `tuple` or `dict`.

## 1. Text and tags

Everything outside a tag is copied to the output literally. There are two tags:

* `{{ expr }}` — interpolation.
* `{% ... %}` — block tag.

Scanning is left to right. `{{` and `{%` always open a tag (there is no way to write a
literal `{{`). A stray `}}`, `%}`, `{` or `%` in ordinary text is literal text.

Inside a tag, single-quoted string literals are respected while looking for the closing
delimiter: a `'` starts a string that ends at the next `'` (there are no escapes), and
`}}` / `%}` inside such a string does **not** close the tag. So
`{{ 'a}}b' }}` is one tag whose expression is `'a}}b'`.

* A tag that is never closed before the end of the template is an error of kind `syntax`.
* A string literal that is never closed is an error of kind `syntax`.

## 2. Whitespace control

An opening delimiter may be written `{{-` or `{%-`, and a closing delimiter `-}}` or
`-%}`. The `-` is not part of the expression (there is no subtraction in this language,
so a `-` immediately before `}}` or `%}` is always whitespace control).

* `{{-` / `{%-` removes **all** whitespace from the end of the run of literal text
  immediately before the tag.
* `-}}` / `-%}` removes **all** whitespace from the start of the run of literal text
  immediately after the tag.

"Whitespace" means what `str.strip()` with no argument strips: spaces, tabs, newlines,
carriage returns, form feeds and vertical tabs. Stripping may consume the whole run.
Two tags with nothing between them have an empty run between them, and stripping never
reaches past a tag into an earlier or later run.

## 3. Expressions

An expression is a primary optionally followed by a filter pipeline:

```
expr    := primary ( '|' filter )*
primary := INTEGER | STRING | PATH
```

Whitespace around the primary, the `|` and each filter name is ignored.

* `INTEGER` — one or more ASCII digits, e.g. `42`. There are no negative literals.
* `STRING` — `'...'`, single quotes, no escapes; the content may not contain `'`.
* `PATH` — dot-separated segments, e.g. `user.name` or `items.0.name`. The first segment
  matches `[A-Za-z_][A-Za-z0-9_]*`; every later segment matches `[A-Za-z0-9_]+`.
* `filter` — a name matching `[A-Za-z_][A-Za-z0-9_]*`.

Anything else (an empty expression, `a b`, `1x`, an empty or malformed filter name such
as in `{{ x | }}`) is an error of kind `syntax`.

**Path resolution.** Start from the context dict and consume segments left to right.
If the current value is a dict and the segment is one of its keys, take that value.
Otherwise, if the current value is a list or tuple and the segment is all digits, take
that 0-based element if the index is in range. In every other case (missing key, index
out of range, indexing an int, etc.) the whole path resolves to the empty string `''`.
So an unresolvable path renders as nothing and is falsy.

**Filters**, applied left to right:

* `upper` / `lower` — the value must be a `str`, else error kind `type`; result is a `str`.
* `len` — the value must be a `str`, `list`, `tuple` or `dict`, else error kind `type`;
  result is an `int`.
* `raw` — leaves the value unchanged; switches escaping OFF.
* `esc` — leaves the value unchanged; switches escaping ON.
* any other name — error kind `filter`.

Escaping is ON unless a `raw`/`esc` filter says otherwise, and the **last** `raw` or
`esc` anywhere in the pipeline decides, whatever position it is in. So
`{{ x | raw | upper }}` is not escaped, and `{{ x | raw | esc }}` is escaped.

**Rendering a `{{ }}` tag.** After the whole pipeline has run, the value must be a `str`
(used as-is), or an `int`/`bool` (rendered with `str()`, i.e. `7`, `True`, `False`);
anything else (a list, tuple or dict) is an error of kind `type`. Then, if escaping is
ON, the string is escaped exactly once, by performing these four replacements in this
order:

```
"&" -> "&amp;"     then     "<" -> "&lt;"     then     ">" -> "&gt;"     then     '"' -> "&quot;"
```

Because `&` is replaced first, an input that already contains `&lt;` renders as
`&amp;lt;`. Escaping happens after all filters, never before or between them.

## 4. Blocks

```
{% if EXPR %} ... {% elif EXPR %} ... {% else %} ... {% endif %}
{% for NAME in EXPR %} ... {% empty %} ... {% endfor %}
```

`{% elif %}` may repeat and is optional; `{% else %}` and `{% empty %}` are optional and
may appear at most once, and only as the last branch. Tag text is whitespace-stripped
and its first word is the keyword. `{% else %}`, `{% empty %}`, `{% endif %}` and
`{% endfor %}` take no argument. `NAME` matches `[A-Za-z_][A-Za-z0-9_]*`.

**`if`.** The branch conditions are evaluated in order and the first one whose value is
truthy (ordinary Python truthiness of the value produced by the pipeline, before any
stringification or escaping) has its body rendered; if none is truthy the `else` body is
rendered, or nothing if there is no `else`.

**`for`.** The iterable expression must produce a `list` or a `tuple`; anything else
(including an `int`, a `str`, a `dict`, and therefore also an unresolvable path, which
produces `''`) is an error of kind `type`. If the sequence is empty, the `{% empty %}`
body is rendered if there is one and nothing otherwise; the loop body is not rendered
and `NAME` is not bound.

Otherwise, for each item, `ctx[NAME]` is set to the item and `ctx["loop"]` is set to a
dict with keys `index` (1-based `int`), `index0` (0-based `int`), `first` (`bool`) and
`last` (`bool`), then the body is rendered. They are read as ordinary paths, e.g.
`{{ loop.index }}` or `{% if loop.first %}`.

**Scoping.** `NAME` and `loop` shadow any context entries of the same name. When the
loop finishes — including when the sequence was empty, when the body is empty, and when
an error propagates out of the body — both bindings must be **restored**: a key that
existed before gets its old value back, and a key that did not exist before is removed.
A nested loop must therefore not disturb the enclosing loop's `NAME` or `loop`, and the
caller's `ctx` dict must be exactly equal to what it was before `render` returns.

## 5. Errors

`TemplateError` subclasses `ValueError` and has an attribute `.kind`, one of:

* `"syntax"` — unclosed tag, unclosed string literal, unknown tag keyword, malformed
  expression or filter name, malformed `{% for %}` header, an argument given to a tag
  that takes none.
* `"unclosed"` — an `if` or `for` block that is still open at the end of the template.
* `"mismatch"` — a structural keyword in the wrong place: `{% endfor %}` closing an
  `if`, `{% endif %}` closing a `for`, `{% elif %}` or a second `{% else %}` after an
  `{% else %}`, `{% empty %}` outside a `for`, or any `{% elif %}`, `{% else %}`,
  `{% empty %}`, `{% endif %}`, `{% endfor %}` with no open block at all.
* `"filter"` — unknown filter name.
* `"type"` — a filter or a `for` or a `{{ }}` applied to a value of the wrong type.

**Precedence.** Work happens in three passes and the first pass to fail decides the kind:

1. **Tokenize** the whole template. Any unclosed tag or unclosed string literal anywhere
   in the text raises `syntax` here, before anything else is looked at.
2. **Parse** the token list into blocks, left to right. For each tag the keyword is
   examined first: an unknown keyword raises `syntax`; a known structural keyword that
   does not fit the current block structure raises `mismatch`; only then are its
   arguments checked (`syntax` if malformed). Expressions are validated during this
   pass for *every* tag, even ones inside a branch that will never be rendered — but
   only their *shape*: `{% if 0 %}{{ }}{% endif %}` raises `syntax`. If the end of the
   token list is reached with a block still open, that raises `unclosed`.
3. **Render.** `filter` and `type` errors are raised here, in the order they are met
   while producing output, so they only happen for parts that are actually rendered:
   `{% if 0 %}{{ x|nope }}{% endif %}` renders `''`.

## 6. Worked examples

```python
render("Hi {{ user.name|upper }}!", {"user": {"name": "ada"}}) == "Hi ADA!"
render("{{ a }}|{{ a|raw }}", {"a": '<b>&"'}) == '&lt;b&gt;&amp;&quot;|<b>&"'
render("{{ a|raw|upper }}/{{ a|esc }}", {"a": "a&lt;b"}) == "A&LT;B/a&amp;lt;b"
render("{% for w in ws %}{{ loop.index }}.{{ w }} {% empty %}none{% endfor %}[{{ w }}]",
       {"ws": ["a", "b"], "w": "keep"}) == "1.a 2.b [keep]"
render("x\n  {%- if items|len -%}\n  {{ items.1 }}\n  {%- endif -%}\n  y",
       {"items": ["p", "q"]}) == "xqy"
render("{{ 'a}}b' }}{% if miss %}A{% elif 1 %}B{% else %}C{% endif %}", {}) == "a}}bB"
```

`test_tmpl.py` is a *partial* check: it does not cover everything in this specification,
and some of its tests already pass on the broken code. Where it is silent, this document
is the authority. The hidden grader tests the whole specification above.

Write a few quick checks of your own and run them with `python`, then reply "done".
