Inspect the Python source files available in the current directory. The target function is
`select_events`.

Decide whether that function does exactly what its docstring claims. Treat the docstring as a
specification: every stated behavior must be true, and an unstated behavior is not a reason to
reject it. Trace every branch that determines whether an item is selected, including the
distinction between string and non-string values, and also check the cap and stopping behavior.
This is a yes-or-no comprehension question, not a request to improve the code.

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
