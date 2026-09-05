# Unknown-name review

Known aliases are deliberately finite. This review records unknown spellings so
that a solver does not generalize from the short-name examples into a global
lowercase or recursive alias policy.

`CORE` is not `platform`; it remains `CORE` after ASCII-space edge removal.
`Svc` is not `service`; it remains `Svc`. `web\t` remains `web\t`, because a
tab is data and the exact alias key is `web`. `\tweb` remains `\tweb` for the
same reason. `platform\t` is a distinct source from `platform`.

Unknown keys are retained after edge-space removal and case folding. Thus
`NewMetric` becomes `newmetric`, `new\tmetric` becomes `new\tmetric`, and a
space-only key becomes the empty key. A global alias is applied only to its
exact canonicalized key; ` err ` becomes `error`, while `\terr` remains
`\terr`. Source-specific aliases are likewise exact after key normalization.

Unknown labels are not rejected. They are edge-space trimmed and case folded;
the only discarded label is one whose canonical value is empty. A tab-only
label is therefore the nonempty label `\t`, while a space-only label is absent.

These facts are not malformed-input behavior. All the values remain strings in
the valid schema. They are included because broad `strip`, source case folding,
and “helpful” alias recursion are plausible but wrong release implementations.
