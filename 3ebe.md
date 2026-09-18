# Console decides colour from stdout but errors are written to stderr, so escapes leak into a redirected stderr
kind: debt
tags: cli
created: 2026-09-18T18:37Z

- 2026-09-18T18:37Z Reproduced on main at a5341ac: with stdout on a tty and stderr redirected, `uv run utina whois nosuchparty 2>/tmp/e.txt` writes `ESC[1;31mERROR` into the file. Cause: `Console.over` sets one `color` flag from `_takes_colour(out, environ)` (src/utina/cli/app.py:123) and `render_error` writes to `console.err` (src/utina/cli/app.py:551), so the out stream's capability decides the err stream's painting. The mirror case is a colourless error when stdout is redirected and stderr is a terminal. Fix shape: decide per stream — carry two Style values, or a `style_for(stream)`, rather than one flag. Being fixed as part of the colour-scheme work (.ignored/color-scheme.md), since it is the same file and the same idea; ticked because the defect stands on today's main independently of that feature.
