# utina cannot fold a GEL it did not write: no serialized GEL format, no loader, and Corpus.load trusts every SAID and signature it is handed
kind: todo
tags: oracle
created: 2026-09-24T15:54Z

- 2026-09-24T15:54Z The largest limit on utina as a cross-implementation oracle: it can only fold records its own constructor wrote in-process. Shape of the fix: (1) a serialized GEL format carrying each event's original signed bytes; (2) a loader that REBUILDS rather than trusts — re-derives every SAID from the bytes, verifies every signature against key state, and admits an event only when local reconstruction reproduces it byte for byte; (3) replay into fresh stores with signing disabled, so ingestion can never mint. Depends on the GEL shape decided under 4uus/5edf, so it comes after them. Complete-inventory closure (tick below) belongs in the same loader. Found by the outside comparison of 2026-09-24.
