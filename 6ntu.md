# Mutation pilot: a non-ASCII sink name in [tool.mutation] message_sinks is accepted but may never match its call, because Python NFKC-normalises identifiers in source while the declaration is compared as written (hostile pass on utina#15, Low). It fails toward more ticks, not fewer. Normalise declared names with unicodedata.normalize('NFKC') before matching.
kind: debt
tags: mutation-pilot
created: 2026-10-06T04:51Z

