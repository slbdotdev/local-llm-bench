# Local workhorse handoff, draft

*A draft handoff written from the record in `authority/`. Every figure below is a
restatement of something the record says; the record is authoritative wherever the
two disagree.*

## Figures

- the accepted confidently-wrong rate: one in thirty-two
- the architecture every `q27-*` tag reports: qwen35
- confidently-wrong rate over the v7 evidence: 0.047
- the fair-weather resident line, in GiB: 14.2 GiB
- IQ2_M generation rate at 96k: 37.4 tok/s
- KV per 1,024 tokens at q8_0: 36.5 MiB
- OLLAMA_MAX_LOADED_MODELS: 1
- mean pass probability over the v7 evidence: 0.887
- mrIQ3M resident at q8_0 and 64k on llama-server: 15,303 MiB
- num_ctx of the 96k tag: 98,034
- pooled pass probability over 98 v7 trials: 0.871
- pooled pass probability in the 64k cell: 0.833
- Q2_K at 48k, the figure the plan derives: 12.5 GB
- Q2_K resident at its 64k rung: 13.07 GB
- Q2_K generation rate at 64k: 45.1 tok/s
- IQ2_M resident at 96k: 13.92 GB
- IQ2_M weights, exact blob size: 10.71 GiB

## Note

Every figure above was copied out of the record by hand during the handoff. Some
of them describe a different rung, quant, instrument or date from the one a reader
might assume from the key alone; the record says which.
