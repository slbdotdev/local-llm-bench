# Label review: canonical first-seen behavior

Labels are emitted for human review, so their order is stable and their spelling
is canonical. The label review used accepted changes with the following lists:

* `[`Urgent`, ` urgent `, ``, `\turgent`]` yields
  `["urgent", "\turgent"]`. The tab is data and is not removed.
* `[`Owner`, `owner`, `Follow-up`]` yields
  `["owner", "follow-up"]`.
* `[` `]` yields `[]`, but the accepted change still increments
  occurrences and may create an entry.

For one key, merge the first accepted list and then later accepted lists from
left to right. Membership is checked on canonical labels, not raw labels. A
later raw spelling that canonicalizes to an existing label is ignored without
moving the existing value. A later new label appends after all earlier labels.

An ignored or void change contributes no labels even if it appears between two
accepted changes. Do not normalize labels before the policy gate as a shortcut;
doing so can make a rejected annotation visible when the same key is later
accepted.

The output owns the label lists. The review harness mutates an output label list
after transformation and verifies that the input change labels are unchanged.
The implementation can use a temporary set for membership, but output order is
always the list's first-seen order.
