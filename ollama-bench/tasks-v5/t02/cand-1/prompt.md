Inspect the Python source files available in the current directory. The target function is
`bounded_indices`.

Decide whether that function does exactly what its docstring claims. Treat the docstring as a
specification: every stated behavior must be true, and an unstated behavior is not a reason to
reject it. You must reason from the source code, not from running an implementation supplied by
the model. Pay attention to boundary values and to whether the returned result includes or
excludes an endpoint.

Create `answer.txt` in the current directory containing exactly these two nonblank lines (with
your own values):

```
ANSWER: <yes-or-no>
EVIDENCE: <line-number>: <the exact source line that proves your answer>
```

Use `yes` only when the implementation and docstring agree completely; otherwise use `no`.
The evidence must name a line number in the source and reproduce that source line exactly apart
from leading/trailing whitespace. Choose the single most decisive line. Do not cite a line from
your answer file, and do not add explanation to `answer.txt`.
