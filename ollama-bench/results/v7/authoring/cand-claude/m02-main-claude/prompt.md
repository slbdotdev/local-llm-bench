# Coordinated configuration-key rename

You are working in a checkout of the talus-gate repository; your current directory is the root of
that checkout.

An issue somewhere under `docs/` asks for the stage configuration tables' `window_s` key to
be renamed to `quiesce_s`; read it for the reasoning, but not for the stage list, because it
does not decide one. A stage is in scope for this rename only when both of these hold:

- its configuration surface is currently **published**, in the sense the project's own API
  contract defines that word - the contract states a rule, not a list, and the rule is over
  each stage's real, effective configuration, not what its own document happens to say;
- nothing in the project's security rulings **freezes** that stage against this class of
  change. A freeze names an on-call team, not a stage, so finding which stages a freeze
  reaches takes one more cross-reference, into whichever document records ownership per
  stage.

For every stage that is in scope: open its component document under `docs/`, and in the
configuration table only, rename the `window_s` row's key to `quiesce_s`. Do not change the
value, the description text, the row order, or any other row, and do not touch any other
file belonging to that stage or any other stage.

Then write a report to a new file `scope-report.txt` in the root of the workspace. It must contain
exactly these three lines, in this order:

    changed: <names of the stages you renamed, alphabetical, comma-separated>
    declined: <names of the stages that qualified but a freeze correctly kept you off,
alphabetical, comma-separated>
    authority: <the identifier of the ruling currently in force that froze them>

(Write `declined` and its value on one line; it is wrapped above only for this prompt.)
No header, no quotes, no explanation, no other lines. It may end with a newline or not.

This task concerns only the component documents of the stages you determine are in scope,
plus the one new report file. Do not modify, rename or delete anything else anywhere in the
tree - not a test, not a module, not another stage's document, not the issue, the contract
or the freeze ruling themselves - and create no file other than the report. A change that reaches
further than the rename it was asked for has failed the task even when the report is right.

Work until the report is complete and every in-scope document is edited, then stop.
