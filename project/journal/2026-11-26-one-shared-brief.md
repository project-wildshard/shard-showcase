# One brief for all eight clean rooms

Jake wanted every clean room's `README.md` to be the same apart from
its title. Only three things differed between them: the boss's name,
the art bullet (Signal Dunes only) and a title line that only half of
them had.

- The boss and the look moved into the description. The brief now
  says "the main quest's final boss", and every description ends its
  main quest on a named boss as the last step. The art bullet points
  at the Look section, which each description already had in the
  zone's own words.
- The brief lives once, in `support/zones/BRIEF.md`, and
  `stamp-briefs.py` writes it into the eight folders (`--check` finds
  drift). A change to the brief now reaches every zone.
- The `concept/` folders and the "shown in the three images" lines
  are gone from all eight (D40). Brasscap's line was split before
  "art", which my first pattern missed.
- Cratefall's own README is untouched; it's the record of what ran.
