# Frontend import review: UI pages F-9 through F-12

The frontend exporter alternates among `web`, `ui`, and the long name with
ordinary spaces. All three resolve to `frontend`, and the first record fixes
the bucket's position. It does not emit lower-case source names by general
case conversion: `WEB` is an unknown source in the current release.

Page F-9 reports `paint` delta 1 `add` with labels `Frame`, `frame`, and a
space-only value. The frontend-specific map turns the key into `render`; its
entry has total 1, occurrences 1, labels `["frame"]`.

Page F-10 reports `draw` delta 2 `adjust` with labels `GPU` and ` gpu `, then
`WARN` delta 0 `add` with an empty label and `Slow`. The first updates render to
total 3, occurrences 2, labels `["frame", "gpu"]`. The second creates a
warning entry with total 0, occurrence 1, labels `["slow"]`. Empty canonical
labels are discarded, but an entry with no labels is still complete and must
contain an empty list.

Page F-11 reports `paint` delta 4 `void` with label `Admin`, followed by
`render` delta -3 `remove` with label `Rollback`. The void is rejected and does
not add `admin`; the remove contributes +3 and updates render to total 6,
occurrences 3, labels `["frame", "gpu", "rollback"]`.

Page F-12 is an empty `ui` record. It merges into the existing frontend bucket
without adding an entry. If no earlier page existed, it would create a visible
empty bucket before any later page.

The frontend review is also a reminder that global key aliases and
source-specific aliases are separate tables. The only frontend-specific aliases
are `paint` and `draw`; `warn` is global and becomes `warning` first.
