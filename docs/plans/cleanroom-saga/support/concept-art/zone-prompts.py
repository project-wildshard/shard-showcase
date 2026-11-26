# Writes 9 concept-art jobs per zone (ZC2): 3 subjects x 3 takes, each job
# reading the zone's ZONE-DESCRIPTION.md (copied in as zone.md).
# Usage: python3 zone-prompts.py <slug> [<slug>...]
import os, shutil, sys

HOME = os.path.expanduser('~')
HERE = os.path.dirname(os.path.abspath(__file__))

SUBJECTS = {
  'a-vista': "SUBJECT: the hero vista: the zone's most iconic wide view, "
             "the first thing that should make a player say wow. Show its "
             "signature landmark and the shape of the land.",
  'b-hub': "SUBJECT: the zone's hub or most important landmark up close "
           "(its town, camp, waystation or centrepiece) with its people "
           "and life, at eye level.",
  'c-fight': "SUBJECT: a combat moment: the hero, seen from behind in "
             "third person (or first person if a ranged weapon is drawn), "
             "fighting the zone's signature enemies or an elite, with the "
             "zone's signature weapon or mechanic in use and the place "
             "readable behind.",
}
TAKES = {
  '1': "TAKE: a clean, readable composition at the zone's signature time "
       "of day.",
  '2': "TAKE: a different time of day or weather that the description "
       "allows, from a lower, more dramatic camera.",
  '3': "TAKE: the most cinematic, cover-art version of the subject.",
}
STYLE = """RULES
- Read zone.md first: it describes the zone, and its look section is
  the art direction. Follow that look exactly: palette, materials,
  light, mood.
- QUALITY BAR: AAA game concept art with rich geometry, dense detail,
  layered depth, nothing empty, nothing placeholder.
- No text, no UI, no HUD, no logos, no watermark.
- Never borrow another style: no neon unless zone.md asks for it, no
  generic steampunk brass, no purple night-blue grading unless the
  zone is set at night.
"""

for slug in sys.argv[1:]:
    desc = f'{HOME}/projects/game-demos/{slug}-clean-room/ZONE-DESCRIPTION.md'
    for subj, what in SUBJECTS.items():
        for take, how in TAKES.items():
            d = f'{HERE}/{slug}/{subj}-{take}'
            os.makedirs(d, exist_ok=True)
            shutil.copy(desc, f'{d}/zone.md')
            prompt = (
                "Use your image generation tool to create ONE landscape "
                "(3:2) image and save it as concept.png in the current "
                "directory. Do not write any other file except model.txt, "
                "holding the exact image model you used (one line).\n\n"
                f"{what}\n\n{how}\n\n{STYLE}"
            )
            open(f'{d}/prompt.txt', 'w').write(prompt)
    print(slug)
