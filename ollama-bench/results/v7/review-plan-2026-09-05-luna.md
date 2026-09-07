REVISE
*Renamed 2026-09-06 from `v7/review-plan-2026-09-07-luna.md`: the campaign labelled rounds by planned campaign day, not by the calendar date they were written.*

1. [BLOCKING] Plan lines 101-116 assign m10-main to Claude, which is both its current main author and not a fresh author under the stated rule, even though the 7/7/6 arithmetic is otherwise correct. Fix m10-main to GLM and change the resulting share to Claude 6, GLM 8, Luna 6, or revise the rule explicitly.

2. [BLOCKING] Plan lines 221 and 236-239 budget four reference arms while section 5.1 carries forward old section 6 and section 8.2 recommends running the missing fifth arm, ZCode. Fix the phase table and estimate to include five arms and z-run, or explicitly defer ZCode and remove the claim that it runs this round.

3. [BLOCKING] Plan lines 8 and 177-183 call the target 10/20 on IQ2_M at 64k, but only the ten main tasks run at 64k while the other ten run on the 24k cheap tag. Fix the headline to say 10/20 across main-at-64k plus cheap-at-24k, or make a main-only 5/10 target.

4. [BLOCKING] Plan lines 55-65 use whole-turn peak input as if it were material occupancy even though calibration section 1 says it includes system prompt, task, prior turns, and tool results, so the 50% gate can pass without 50% of the material being read. Fix the rule to name this as a peak-input proxy and add a material-attribution check, or defend a non-paddable proxy operationally.

5. [BLOCKING] Plan lines 67-82 set new 6-seed, 3-hop, and 5-path thresholds without a cited derivation, while current pibench records only tool-name counts and no event arguments or paths. Fix the thresholds with a cited calibration or decision basis and specify the event schema plus bash-path normalization and validation before relying on read_paths.

6. [BLOCKING] Plan lines 197-220 say a failed gate is re-authored and re-swept, but do not require the unchanged section 3 cross-review and two-reviewer acceptance for that replacement candidate. Fix phase 4 to repeat the required blind review, acceptance, and register update before the candidate is admitted.

7. [NON-BLOCKING] Plan line 22 attributes zero read calls and nine bash calls for m09-main to calibration section 1, which contains the median counts but does not state that m09-specific figure. Remove the unsupported figure or cite the artifact that contains it.

8. [NON-BLOCKING] Plan line 249 says four reads out of 91 files, while calibration section 1 gives a 91-95-file tree. Fix it to say four of 91-95 files, or identify the exact m09 tree if 91 is intended.

9. [NON-BLOCKING] Plan lines 120-129 say BrowseComp and BrowseComp-Plus repository terms do not grant source documents, but the survey assigns that statement only to Plus and says BrowseComp terms and corpus licences require review. Split the two clauses exactly as the survey does.

10. [NON-BLOCKING] Plan line 124 calls every excluded family contaminated or licence-restricted, but the survey mixes restricted, unclear, and terms-requiring-inspection statuses. Replace that label with the survey's mixed categories.

11. [NON-BLOCKING] Plan lines 154-161 say a turn is a tool call, but pibench increments turns on assistant message_end and tool_calls on tool_execution_start as separate fields. Explain the distinction and derive the corrected ceiling from tool_calls rather than redefining turns.

12. [NON-BLOCKING] Plan sections 2.5 and 5.3 do not carry calibration section 11's caveat that m05-cheap-glm was correct at the 300-second timeout with stop_reason toolUse and that timeout must be reported beside the verdict. Add timed_out and stop-reason reporting to the run fields and headline tables.

13. [NON-BLOCKING] Plan section 5 omits calibration section 4's neighbour main-band occupancy range of 9-37% of material and section 4's D7-42 artifact showing Q2_K's silently corrupted Zoé diacritic. Add both as calibration diagnostics so the neighbour comparison carries the same traversal and environment evidence as the workhorse.
