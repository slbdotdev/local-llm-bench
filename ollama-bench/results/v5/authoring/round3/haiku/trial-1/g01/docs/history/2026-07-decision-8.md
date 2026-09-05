# 2026-07 decision record: valid-input boundary

Decision D-48: the adapter contract is defined for valid records only, and the
public function performs no file, network, or package discovery.

A record is a dictionary with string source and list changes. A change has
string key and action, integer delta, and list-of-string labels. The benchmark
does not ask the implementation to report malformed data or fill missing
fields. Direct field access is therefore part of the intended small solution.

Context: callers tried to make the reducer an all-purpose validator. That grew
output and introduced defaults that were absent from the release contract. The
production boundary validates before calling the fold. Keeping the benchmark
at that boundary makes behavior deterministic and keeps the answer short even
though the material to reconcile is large.

Consequences: a conforming solution may use only standard Python operations and
must not import the seed package at runtime. It must preserve the input and
return the exact public shape. Any behavior for malformed input is outside the
question and is not a hidden convention.

This decision also explains why configuration values are included as seed
material: they are evidence to read while authoring, not files the contestant's
function should open during grading.
