# Writes the 9 Brasswick concept-art jobs (CR4): 3 subjects x 3 takes.
import os, shutil

HOME = os.path.expanduser('~')
CF = f'{HOME}/projects/game-demos/showcase-zone-clean-room/docs/media/golden/now'
KS = f'{HOME}/projects/games/wildshard-singleplayer/art/showcase-template/round-11-remaster'
OUT = os.path.dirname(os.path.abspath(__file__)) + '/showcase'

STYLE = """ART DIRECTION
A finished piece of game concept art for a stylised third-person
action RPG that feels like an MMO zone. Style: SIMPLE BUT POLISHED
stylised 3D, like a finished, well-funded stylised action game: clean
readable shapes, bevelled and rounded edges, soft hand-tuned materials,
toy-like charm, saturated but tasteful colour, crisp warm sunlight with
soft shadows and ambient occlusion, a bright blue sky with a few soft
clouds, light atmospheric depth. The identity is a WORKSHOP / TEST-YARD
town in a warm ORANGE and cool GREY palette with small cyan accents:
painted steel, warm sandstone-orange walls with grey steel caps, cream
and grey render, orange tiled roofs, timber, canvas awnings striped
orange and grey, safety stripes, bunting, banners, planters and small
trees, lamps, pennants, signage with personality. Friendly worker
robots (rounded grey bodies, orange hi-vis vests, big yellow visor
eyes, hard hats) live in town.

QUALITY BAR: AAA density and craft: rich geometry, lots of small
props and detail, layered depth, nothing empty, nothing placeholder.

AVOID: neon, glowing blue-cyan floor strips, purple or night-blue
grading, brass-and-gold steampunk gadgetry, dark moody colour, any
text other than one or two short shop signs, any game HUD or UI.
"""

JOBS = {
  'a-square': dict(ref='03-town-square-morning.jpg', ks='west/w01.jpg', subject=
    "SUBJECT: Brasswick's town square in the morning. A cobbled plaza with a "
    "landmark at its centre (a tall clock-and-beacon spire of orange stone "
    "with grey steel bands over a fountain ring), houses and shops around it, "
    "worker robots and a few townsfolk, market stalls. The hero, a young "
    "adventurer with a scarf and an orange backpack, stands in the plaza "
    "seen from behind, third person."),
  'b-gate': dict(ref='07-blast-wall-gate.jpg', ks='west/m01.jpg', subject=
    "SUBJECT: the Blast Wall gate at the east edge of Brasswick: a tall "
    "industrial wall of grey steel panels with orange safety-striped tops, "
    "its heavy sliding blast door half open with warning lights, guard "
    "posts and banners; beyond it the Crate Fields, open ground of stacked "
    "cargo crates and small robots in the distance. The hero walks toward "
    "the gate, seen from behind."),
  'c-fight': dict(ref='08-crate-fields-fight.jpg', ks='west/w01.jpg', subject=
    "SUBJECT: a fight in the Crate Fields just outside town: the hero, "
    "seen from behind over the shoulder, swings a sword at a pack of "
    "characterful toy-like orange-and-grey combat robots (small crate-bodied "
    "critters on springy legs, a low wide forklift charger) with cyan eyes "
    "and readable glowing telegraphs; sparks and dust on the hit; stacked "
    "crates, cranes and the town wall behind."),
}

TAKES = {
  '1': "TAKE: keep the attached in-game screenshot's camera, composition "
       "and where each mass sits, but repaint everything in the art "
       "direction above. The screenshot shows the right level of detail "
       "and density; its colours, lighting, neon and gadgets are wrong.",
  '2': "TAKE: use the first attached image (an in-game screenshot) for "
       "layout and density, and the second attached image (a mockup) as "
       "the reference for palette, materials and charm. Ignore any UI in "
       "either image.",
  '3': "TAKE: a fresh, more cinematic composition of the same subject, "
       "wider, with golden mid-morning light. The attached screenshot is "
       "only a reminder of what the place contains.",
}

for job, spec in JOBS.items():
    for take, how in TAKES.items():
        d = f'{OUT}/{job}-{take}'
        os.makedirs(d, exist_ok=True)
        shutil.copy(f'{CF}/{spec["ref"]}', f'{d}/ref-1.jpg')
        if take == '2':
            shutil.copy(f'{KS}/{spec["ks"]}', f'{d}/ref-2.jpg')
        prompt = (
            "Use your image generation tool to create ONE landscape (3:2) "
            "image and save it as concept.png in the current directory. "
            "Do not write any other file. Write the exact image model you "
            "used into a file model.txt (one line).\n\n"
            f"{spec['subject']}\n\n{how}\n\n{STYLE}"
        )
        open(f'{d}/prompt.txt', 'w').write(prompt)
        print(d)
