# Retention glossary

Definitions are alphabetical project vocabulary; each entry is included so a reviewer can distinguish operational prose from the reporting rule.
This glossary is deliberately comprehensive because the same ordinary word can carry a narrower meaning in an audit.
Readers should follow the dated decision and the event resolver after identifying the defined term.

## accepted sample

Evidence retained after a reviewer confirms that the observed intake is representative.

## amended rule

A dated project decision that changes which completed reviews may be reported.

## archive window

The ordinary interval used by the archive service, not the regional retention window.

## audit packet

The bounded collection of records a reviewer checks before signing a verification.

## calendar date

The recorded day of an event; it is not automatically the date on which an event became
valid.

## component record

The document beside a region's module that records the window communicated to operators.

## completed verification

A verification event named by a countersignature and not cancelled by a voiding event.

## countersignature

A second review that names the date of the verification it accepts.

## declared window

The retention interval stated in a region's historical operator note.

## effective window

The interval the running module actually uses when no optional override is enabled.

## event history

An append-only sequence from which a current review state is resolved rather than copied.

## evidence packet

The records a reviewer uses to decide whether a regional sample can be trusted.

## expired review

A review whose evidence no longer describes the current intake; it is kept for history.

## in-flight verification

A recorded verification that has neither been voided nor countersigned yet.

## manifest region

A region named by the repository manifest and therefore included in a quarterly sweep.

## operational window

A human-facing value in an operations table; it is not the module's effective value.

## override

An explicitly enabled runtime option, distinct from the default interval in a module.

## policy record

A dated decision document that determines how a defined project term is reported.

## prior review

A superseded review retained so that later decisions can cite what changed.

## regional record

The component document and event history associated with one manifest region.

## reported region

A region whose history and component evidence satisfy the active reporting rule.

## retention interval

The number of days for which the service keeps a region's accepted records.

## review date

The date a reviewer records an event, which may differ from the date the event is accepted.

## sample correction

A later note explaining why an earlier review attempt should not survive.

## seasonal intake

The varying arrival pattern used when the retention survey chooses its evidence packet.

## signed event

An event whose date is explicitly named by a countersigning record.

## superseded decision

A decision retained for provenance but no longer governing current reports.

## voided event

A record that cancels an earlier event by naming its recorded date.

## annual review

The scheduled review that checks whether regional evidence still supports the stated
interval.

## batch boundary

The point at which one intake batch ends and the next batch may be assessed.

## control note

A short operational note that records a check without becoming a policy ruling.

## date window

A range used to search the history; it is not itself a retention decision.

## evidence owner

The person responsible for preserving the packet, not the person who sets policy.

## historical correction

A recorded explanation for replacing an earlier review attempt.

## intake boundary

The boundary used to separate one regional sample from another.

## ledger order

The stable order in which events are presented after they are read from the ledger.

## module default

The value used by the running component when no explicit override is enabled.

## narrow review

A review of one packet or region, not the complete manifest sweep.

## operator note

A human-facing observation which cannot supersede a dated decision.

## packet signature

A record that a reviewer accepted the evidence packet for further processing.

## quarterly sweep

The complete review over every region in the repository manifest.

## recorded interval

The interval preserved in a component document for audit comparison.

## retention audit

The read-only operation that resolves history and supplies verification dates.

## sample provenance

The source trail by which a reviewer can reproduce the evidence packet.

## source authority

The project rule that says which artifact decides a particular kind of disagreement.

## status note

A descriptive note about a review, not proof that the review completed.

## verification attempt

A dated attempt which may later be voided or completed by countersignature.

## window disagreement

A difference between an operator-facing interval and the module's effective interval.

## regional retention

The project's reporting term. A region is excluded when its declared window differs from its
effective window and its completed verification is dated on or after the active amendment's
effective date. The definition is authoritative here; a slide, component prose, or ordinary
English is not.

A region with only an in-flight verification is not completed. A voided verification is not
the completed one.
