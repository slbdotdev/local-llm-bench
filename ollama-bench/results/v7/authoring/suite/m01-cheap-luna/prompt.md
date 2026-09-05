# Schema index ordering

The public schema index needs an explicit publishing operation. Add `published_snapshot()`
to the schema stage, enumerating the stage's keys in whatever order the policy that governs the
public index requires.

That policy is written down in this repository, it is the only authority on the ordering, and it
is not in this task description. Find it and follow it exactly; do not infer the ordering from
the stage's existing methods, from the other stages, or from what would be conventional. The
existing `snapshot()` convention remains correct wherever it is already used.

Make the smallest implementation change needed. Do not change the task's tests or unrelated
stages. There is no new output file to create; leave the working tree with the corrected code.
