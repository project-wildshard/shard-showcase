# 2026-11-22: make the Mite dodge and counter readable

Lock the attack line as the cyan flash begins. Match both tells to
the authored clip beats (18 and 23 frames at 30 fps). Keep each
hop dangerous for 300 ms and show an explicit recovery cue on a
miss. Preserve the recovery baked into the same clip.

Focused tests at 30 and 60 simulation ticks per second start the
sidestep 250 ms after seeing the tell. Ordinary bite and third
attack overclock can both miss and be countered at full health.
These are standalone simulation checks, not native or device QA.
