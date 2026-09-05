# Configuration provenance

The release values appear in JSON snapshots because operations reviews the
configuration separately from Python code. The Python release-data module is
the build-time view of those same snapshots. A conforming implementation must
use the values and procedure, not guess a larger alias vocabulary from names
mentioned in old history.

Source table provenance: platform is the target for core, service for svc,
frontend for web and ui, and worker for jobs and batch. Lookup is exact after
ASCII edge spaces, with no source casefold and no recursive target lookup.

Global key table provenance: err/error, warn/warning, lat/latency,
dur/duration, and cfg/config. Local table provenance: platform compile and
compilation/build; service request and req/requests; frontend paint and
draw/render; worker job and task/jobs. Key procedure is edge-space trim,
casefold, one global lookup, one local lookup.

Policy provenance: add one, remove minus one, adjust one, hold zero; ignore and
void rejected. A rejected change has no state effect after its record's source
bucket is ensured. An accepted zero contribution still creates or updates an
entry, counts, and merges labels.

If a history note conflicts with the snapshots or current package, its release
number marks the superseded behavior. If two current views repeat a rule, the
repetition is corroborating evidence. The benchmark asks for the current
release and provides no runtime configuration file to open.
