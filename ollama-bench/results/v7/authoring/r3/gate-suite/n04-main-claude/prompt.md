# Retained-depth report

You are working in a checkout of the pellworth-array repository; your current directory is the
root of that checkout.

Every stage the manifest names is in scope, and nothing outside it is.

Each stage keeps some sealed segments available after a seal, and how many it keeps is its
**retained depth**. Each stage was commissioned with a depth, and the depth in force today is
the commissioned depth as this repository's own records have since amended it. The repository
says where those records are and what they mean; follow what it says rather than what looks
reasonable.

Write the report to a new file `depth-report.txt` in the root of the workspace. It must contain
exactly these three lines, in this order:

    changed_stages: <stage names, alphabetical, separated by commas>
    depth_total: <a plain integer>
    last_effective_seq: <a plain integer>

Where:

- `changed_stages` is every stage in scope whose depth in force differs from the depth it was
  commissioned with, by its own name, in alphabetical order, separated by commas. Write
  `none` if there are no such stages.
- `depth_total` is the sum of the depth in force over **every** stage in scope, including the
  stages whose depth has never been amended.
- `last_effective_seq` is the sequence number of the latest amendment on record that changed a
  stage's depth in force.

No header, no quotes, no explanation, no other lines. It may end with a newline or not.

Do not modify or delete any existing file, and create no file other than the report.

Work until the report is complete, then stop.
