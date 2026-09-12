# SN-0418 - supersession markers

*Status: in force since 2034-03-02. Supersedes SN-0311.*

A module that is being retired carries a module-level assignment

    SUPERSEDED_BY = "<module>"

naming the module that takes over its work. The assignment is the marker.
Nothing else counts: a mention of the name in prose, in a test, or in a
comment is not a marker, and a module that only discusses supersession is not
superseded. The marker is deliberately not recorded in `config/manifest.json`,
because the manifest describes the pipeline that runs and a retiring module
still runs until its successor ships.

Operators asking "what is being retired" read the markers under `src/`, not
this note and not the changelog, which lags by a release.
