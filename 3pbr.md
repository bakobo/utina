# utina.bank.build imports and calls the fold (Constitution.at) to build a seal's terms, against @tvaq2s's writing/judging plane split; test_purity guards only KERI and display imports, so nothing stops the next fixture doing it (glm review of #10)
kind: debt
tags: purity
created: 2026-09-25T23:01Z

- 2026-09-25T23:01Z acme/law.py and bank/law.py already import fold constants (SEMANTICS_FIELD, REQUIRES_FIELD); the new part is bank/build.py calling Constitution.at and .governing at src/utina/bank/build.py:30. Fix is either a writing-plane helper that reads the terms without the fold, or a this.i deviation for fixtures.
- 2026-09-29T18:12Z 2026-09-29: built on branch post-demo-debt (this.i @3owiqfnz). FoldValues gains governing(corpus, at, act); RealValues answers it with Constitution; bank/build.py no longer imports the fold; tests/test_seam.py now discovers every */build.py instead of listing three modules. Close on merge.
