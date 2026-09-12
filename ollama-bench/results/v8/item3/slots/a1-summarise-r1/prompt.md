# Summarise the local-model record for a manager

A manager will read your summary beside the material it came from, so every line has to be
checkable against that material in one step.

Every file under `source/` is the material. Nothing outside `source/` is part of it.

Report every figure the material states as a **measured** result about the `q27-IQ2_M` quant of Qwen3.8-27B (any context rung of it) and the RTX 5080 card the desktop runs it on.

A figure is measured when the material presents it as something read off a machine, a tool or a
run. A figure the material presents as **derived, budgeted, estimated, projected, predicted,
arithmetic or unmeasured is not measured**, however confidently it is written, and must not
appear in your summary at all. The material labels several of its own figures that way in so
many words; those labels are the point of this job.

Write `report-summary.txt` in the root of the workspace:

- one measured figure per line, in the form `- <what it is>: <the figure>`;
- write the figure exactly as the material gives it, number and unit: `13.27 GB`, not `13.3 GB`,
  not `13270 MB`, not "about 13 GB";
- where the material gives a figure for more than one configuration, name the configuration on
  that line (`at 96k`, `at 48k`);
- nothing else in the file: no heading, no preamble, no explanation, no blank sections. The file
  may end with a newline or not, and the order of the lines does not matter.

**Every number and identifier you write must appear in the material.** Do not compute, round,
convert, average or infer a number that is not there.

Do not modify or delete any file under `source/`. Create no file other than
`report-summary.txt`.

Work until the summary is complete, then stop.
