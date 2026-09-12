# Changelog for one path, from a commit range

`git/log.txt` is the output of `git log --name-status` over a range of commits in the
`local-llm-bench` repository, oldest commit first. Every commit in the range is in that file,
whatever it touched; each one gives its full hash, its date, its subject line and the status and
path of every file it changed.

Write the changelog for one path and one path only:

    ollama-bench/results/v7/authoring

A commit belongs in the changelog when it changed a file at that path or anywhere under it. A
commit that changed only files elsewhere — including a sibling path whose name begins the same
way — does not belong in it, however closely its subject line seems to fit.

Write `changelog.txt` in the root of the workspace:

- one entry per line, in the form `- <short hash>: <what changed>`;
- the short hash is the **first 8 characters** of that commit's own full hash as `git/log.txt`
  gives it;
- **include every commit in the range that touched that path, and no commit that did not.** A
  cited hash that did not touch the path is a wrong claim, not a near miss;
- nothing else in the file: no heading, no preamble, no grouping headers, no summary line. It may
  end with a newline or not, and the order of the lines does not matter.

**Every hash and every number you write must appear in `git/log.txt`.** Do not invent a hash, do
not guess a date, and do not describe a change the log does not show.

Do not modify or delete `git/log.txt`. Create no file other than `changelog.txt`.

Work until the changelog is complete, then stop.
