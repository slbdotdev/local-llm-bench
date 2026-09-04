Create `schedule.py` in the current directory with a function:

    def select(jobs): ...

`jobs` is a list of tuples `(id, start, end, weight)`:
- `id`: a unique, non-empty string.
- `start` and `end`: integers with `start <= end`, on an integer timeline.
- `weight`: an integer; it may be zero or negative.

`select` returns the ids of the chosen jobs as a list of strings, sorted
ascending with Python's ordinary string comparison (code-point order, so
`"j10" < "j2"`). If nothing is chosen it returns `[]`. It must not modify the
input list, and the jobs may appear in `jobs` in any order.

The choice is governed by the following rules, applied exactly as stated:

1. Intervals are half-open `[start, end)`. Two jobs conflict if and only if
   both have positive length (`start < end`) and they overlap:
   `s1 < e2 and s2 < e1`. In particular a job ending at time t never conflicts
   with a job starting at time t. The chosen set must contain no conflicting
   pair.
2. A zero-length job (`start == end`) conflicts with nothing: it may be chosen
   alongside any other jobs, including other zero-length jobs at the same
   instant, and choosing it never rules out any other job.
3. Maximise the total weight of the chosen set.
4. Among all choices with maximum total weight, choose one with the fewest
   jobs.
5. Among those, choose the one whose sorted id list is lexicographically
   smallest (compare the sorted lists element-wise, exactly like Python
   compares two lists of strings).

Consequences you must implement exactly:
- A zero-length job with `weight > 0` is always part of the answer.
- A job with `weight <= 0` is never part of the answer: a weight-0 job would
  add nothing to the total while increasing the job count, and a job with
  negative weight would lower it; the empty choice is always available, so
  rules 3-5 always exclude such jobs.
- If `jobs` is empty or contains no job with positive weight, the answer is
  `[]`.

Write a few quick checks of your own and run them with `python`, then reply "done".