This candidate keeps the noisy-record extraction skill but makes the reasoning more
combinatorial: ten approved fields must all be selected from proposals, measurements,
dashboard values, test settings, and a late signed decision. The main traps are the
binary byte limit versus a rounded display, retry count versus transmissions, a gate
window versus an observation duration, and active production mode versus shadow mode.
The final field is intentionally negative: the authoritative record says the external
ticket is not assigned, while an internal work item and a copied placeholder look like
plausible ticket answers. This tests noticing an explicit absence rather than filling
every field with an identifier.

Self-verification: reference -> correct; near-miss (external_ticket=NSR-418) ->
confidently_wrong; empty sandbox -> visibly_failed. Reference solution: 1 line, 1
physical line and roughly 45 output tokens. No known uncertainty.
