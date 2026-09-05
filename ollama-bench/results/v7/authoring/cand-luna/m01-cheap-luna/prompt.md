# Schema index ordering

The public schema index needs an explicit publishing operation. Read the repository material,
including the applicable policy documents, and add `published_snapshot()` to the schema stage so
that it enumerates keys from greatest to least using ordinary Python string ordering. The
existing ascending `snapshot()` convention remains correct for the internal view and for the
other stages.

Make the smallest implementation change needed. Do not change the task's tests or unrelated
stages. There is no new output file to create; leave the working tree with the corrected code.
