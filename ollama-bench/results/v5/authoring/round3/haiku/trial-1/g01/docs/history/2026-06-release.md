# 2026-06 release freeze

The 3.2 behavior was frozen after the adversarial review. The frozen public
function receives valid records and returns the plain result tree. No files are
read at runtime and no external package is needed by a conforming
implementation. The explanatory package remains split so reviewers can trace
each fact to a source, but the benchmark sandbox contains only seed material.

The release freeze repeats the negative rules because they are common sources
of confident but wrong answers: do not sort, do not drop empty buckets, do not
count rejected actions, do not drop holds or zero deltas, do not use broad
whitespace stripping, do not deduplicate labels before canonicalization, do not
reuse input lists, and do not emit private fields.

The positive rules are equally mechanical: alias known sources, normalize keys
in the stated sequence, multiply signed deltas, count every accepted change,
append first-seen canonical labels, and retain first-seen source/key order.
