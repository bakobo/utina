# A demo beat pause with no stdin raises an uncaught EOFError traceback instead of a coded error
kind: debt
tags: cli
created: 2026-09-18T19:07Z

- 2026-09-18T19:07Z Repro: `utina demo2 --part live < /dev/null` exits 1 with a traceback ending in `EOFError: EOF when reading a line` from `_wait_for_a_keypress` (src/utina/cli/app.py:106). Same for `utina demo` without --no-pause. Every other failure in this CLI leaves through one door carrying a bakobo.errors code and plain sentences; this one leaves as a Python traceback, which is the shape the error standard exists to forbid. Low priority for the demo itself — a narrator in a terminal has a tty, and piping stdout does not close stdin — but it is reachable from nohup, cron, or any harness that closes stdin, and a traceback is the worst thing that could appear on a projector. Fix shape: treat EOF as 'nobody is there to press a key' and fall through to no-pause, which is the behaviour a non-interactive console already has via _no_pause.
