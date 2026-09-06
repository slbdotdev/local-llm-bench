# Rename an aliased operation

You are working in a checkout of the ember-course repository; your current directory is the root of
that checkout.

Elsewhere in this tree, alongside the generated pipeline stages, a small subsystem bridges
one pipeline stage's own recovery operation to a second, outward name for the support
tooling that talks about it. The subsystem consists of a bridge module, a lookup table, a
serializer, a documentation example and a regression test, and it is bound to exactly one
pipeline stage. Which stage, and what name the subsystem currently uses, is not stated here;
the subsystem's own material says how that stage is identified, and working that out is part
of the task.

External support tooling has started calling this operation `rehydrate`. Rename it, from whatever
the subsystem currently spells it as, to `rehydrate`, everywhere the subsystem itself spells the
old name - in the bridge module, the lookup table, the serializer, the documentation example
and the regression test, and in one further place: a single string value inside a small
configuration file, easy to pass over among many unrelated entries, that also carries the
old name.

Do not rename anything outside this subsystem. In particular: the bound stage's own module
keeps its own verb under its own name and is not touched; one or more other, unrelated
stages' own modules happen to define a method of the very same old name, for an unrelated
purpose, and are not touched either; and a withdrawn decision record elsewhere mentions the
old operation once, in its own different words, as history - it is evidence, not live code,
and it is not touched.

Once the rename is complete, write a report to a new file `rename-report.txt` in the root of the workspace.
It must contain exactly these four lines, in this order:

    symbol_old: <the name you renamed, exactly as the subsystem originally spelled it>
    symbol_new: <the name you renamed it to>
    bound_module: <the path of the pipeline module the subsystem binds to>
    sites: <the paths of every file you changed, alphabetical, comma-separated>

No header, no quotes, no explanation, no other lines. It may end with a newline or not.

This task concerns only this subsystem's own files. Do not modify, rename or delete anything
else anywhere in the tree, and create no file other than the report.

Work until the rename and the report are both complete, then stop.
