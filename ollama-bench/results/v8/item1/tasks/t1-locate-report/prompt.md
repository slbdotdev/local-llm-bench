# Which modules are marked as superseded

You are working in a checkout of the halyard-mesh repository; your current directory is the root
of that checkout.

Some modules under `src/` carry a marker saying they are being retired. The project has a note
that defines exactly what that marker is and what does not count as one. Find the note, then find
every module that actually carries the marker.

Write your answer to a new file `findings.txt` in the root of the workspace. Give one
`key: value` line for each of these three keys, in any order:

    modules: the file names of the marked modules, with the `.py` suffix and no directory,
             separated by commas
    count:   how many there are, as a plain integer
    note:    the identifier of the note that defines the marker

Nothing else in the file. Do not modify or delete any existing file, and create no file other
than `findings.txt`.
