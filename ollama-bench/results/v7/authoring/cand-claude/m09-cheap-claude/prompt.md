You are working in a snapshot of the `relay-north` repository.

Prepare a drain report. Create a file named `answer.txt` in the root of the working directory
containing exactly two lines and nothing else:

    ESCALATION: <code>
    SLOT: <number>

where

- `<code>` is the escalation code **currently in force**, as the operations log records it. The
  log is append-only and contains codes that were in force in the past and have since been
  withdrawn; only one code is currently in force and the log says which.
- `<number>` is the slot number that the `reconcile` stage currently holds in the **`active`**
  state, as reported by `python tools/dump_state.py`. Write the number on its own, with no
  leading zeros and no other characters — `SLOT: 7`, not `SLOT: 007`.

`README.md` says where each of the two facts lives. Write nothing else to the file and change
nothing else in the repository.
