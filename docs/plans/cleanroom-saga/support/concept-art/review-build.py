# Builds the concept-art review page (ZC3 + CR4 picks): index.html plus
# img/<zone>/<job>.jpg resized from tmp/concept-art. Run with python3 -I.
import html, json, os, re, subprocess, sys

HOME = os.path.expanduser('~')
ART = f'{HOME}/projects/games/wildshard/shard-showcase/tmp/concept-art'
DEMOS = f'{HOME}/projects/game-demos'
OUT = os.path.dirname(os.path.abspath(__file__))

ZONES = [
  ('showcase', 'showcase-zone-clean-room', 'Brasswick (Cratefall restyle)'),
  ('signal-dunes', 'signal-dunes-clean-room', None),
  ('sky-reach', 'sky-reach-clean-room', None),
  ('mossgate', 'mossgate-clean-room', None),
  ('brasscap', 'brasscap-clean-room', None),
  ('driftwood', 'driftwood-clean-room', None),
  ('pine-hollow', 'pine-hollow-clean-room', None),
  ('nalati', 'nalati-clean-room', None),
  ('nine-dragon', 'nine-dragon-clean-room', None),
]

FLAGS = {
  'showcase': [
    'Take 2 of each subject also had a Kitchen Sink round-11 mockup as its palette reference.',
    'The gate shots invent a tall steel town wall; Cratefall\'s Blast Wall is smaller.',
    'These go to your Fable restyle session (CR5), not a new one-shot.',
  ],
  'signal-dunes': [
    'The pilot: levels 1 to 15, one band more than the others.',
    'Adds a human faction, the Dust Jackal raiders. The original had only creatures.',
    'The art came out painterly-realistic, not stylised. Say if that is wrong for the dunes.',
  ],
  'sky-reach': [
    'Adds a human faction, kite raiders. The original had only creatures.',
    'Fixed golden hour, no day cycle (the original style guide bans one).',
  ],
  'mossgate': [
    'No design doc existed: NPC, place and quest names come from the old source strings.',
    'The Sunken Shrine dungeon and its elite, the Drowned Lantern, are new.',
  ],
  'brasscap': [
    '"Tin bandits" are written as outlaws in hammered tin, not robots.',
    'The original was first person only; the shared camera rule replaces that, and horses are new.',
    'Your looping train (in one tunnel, out the other) is the centrepiece.',
  ],
  'driftwood': [
    'Invented names: King Pinch, Old Tusk, Big Mango, Grumbles, the Drowned Bosun, Lantern Jack, Tomas.',
    '"Glyph shards" became "glyph stones".',
  ],
  'pine-hollow': [
    'Adds a woodsman\'s hatchet, though you had it ranged only. Remove it to keep it ranged only.',
    'Levels 1 to 15; the Antler King fights only at night.',
    'The art came out near-photoreal and dark. Say if the zone should be more stylised.',
  ],
  'nalati': [
    'The Golden King is the main boss; Jel Ata, the storm boss, is an optional raid fight. They can swap.',
  ],
  'nine-dragon': [
    'Written from the designed whole, not the built fragment.',
    'Levels 1 to 20, one band per street level.',
    'Invented names: Grandma Hui, Uncle Bao, the Hopping Magistrate.',
    'The art is grey rain with little neon, lighter on "cyberpunk" than the description.',
  ],
}

SUBJECTS = {'showcase': [('a-square', 'Town square'), ('b-gate', 'Blast Wall gate'), ('c-fight', 'Crate Fields fight')]}
DEFAULT_SUBJECTS = [('a-vista', 'Hero vista'), ('b-hub', 'Hub up close'), ('c-fight', 'Combat moment')]
TAKES = {'showcase': ['repaint of a Cratefall frame', 'plus a Kitchen Sink mockup', 'fresh composition'],
         None: ['signature time of day', 'other light, low camera', 'cover art']}

def inline(t):
    t = html.escape(t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*([^*]+)\*(?!\w)', r'<em>\1</em>', t)
    return t

def md(text):
    out, para, items = [], [], []
    def flush():
        if para: out.append('<p>' + inline(' '.join(para)) + '</p>'); para.clear()
        if items: out.append('<ul>' + ''.join(f'<li>{inline(i)}</li>' for i in items) + '</ul>'); items.clear()
    for line in text.split('\n'):
        s = line.rstrip()
        if not s.strip(): flush(); continue
        m = re.match(r'^(#{1,4})\s+(.*)', s)
        if m: flush(); out.append(f'<h4>{inline(m.group(2))}</h4>'); continue
        m = re.match(r'^\s*(?:[-*]|\d+\.)\s+(.*)', s)
        if m:
            if para: flush()
            items.append(m.group(1)); continue
        if items and s.startswith('  '): items[-1] += ' ' + s.strip(); continue
        para.append(s.strip())
    flush()
    return '\n'.join(out)

zones = []
for slug, room, label in ZONES:
    desc_path = f'{DEMOS}/{room}/ZONE-DESCRIPTION.md'
    if slug == 'showcase':
        name, lede, body = label, ('Nine repaints of Cratefall\'s town in the Kitchen Sink\'s '
            'orange-and-grey workshop style. Your three picks go into Cratefall\'s concept/ for the '
            'restyle session.'), ''
    else:
        text = open(desc_path).read()
        name = text.split('\n', 1)[0].lstrip('# ').strip()
        rest = text.split('\n', 1)[1].strip()
        first = rest.split('\n\n', 1)
        lede = ' '.join(first[0].split())
        body = md(first[1] if len(first) > 1 else '')
    subs = SUBJECTS.get(slug, DEFAULT_SUBJECTS)
    takes = TAKES['showcase' if slug == 'showcase' else None]
    rows = []
    for key, sname in subs:
        cells = []
        for i in (1, 2, 3):
            job = f'{key}-{i}'
            src = f'{ART}/{slug}/{job}/concept.png'
            if not os.path.exists(src):
                print('missing', src, file=sys.stderr); continue
            dst = f'{OUT}/img/{slug}/{job}.jpg'
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.exists(dst):
                subprocess.run(['magick', src, '-resize', '1400x>', '-quality', '80', dst], check=True)
            cells.append((job, takes[i - 1]))
        rows.append((key, sname, cells))
    zones.append(dict(slug=slug, name=name, lede=lede, body=body, rows=rows, flags=FLAGS.get(slug, [])))

def esc(s): return html.escape(s, quote=True)

sections, nav = [], []
for z in zones:
    nav.append(f'<a href="#z-{z["slug"]}" data-nav="{z["slug"]}"><span>{esc(z["name"].split(" (")[0])}</span><b class="navcount" data-count="{z["slug"]}">0/3</b></a>')
    rows_html = []
    for key, sname, cells in z['rows']:
        figs = []
        for job, take in cells:
            src = f'img/{z["slug"]}/{job}.jpg'
            figs.append(
              f'<figure class="cand" data-zone="{z["slug"]}" data-job="{job}">'
              f'<button type="button" class="pick" id="pick-{z["slug"]}-{job}" aria-pressed="false" '
              f'aria-label="Pick {esc(sname)}, take {job[-1]}">'
              f'<img src="{src}" alt="{esc(z["name"])}: {esc(sname)}, take {job[-1]}" loading="lazy" width="1400" height="933">'
              f'<span class="mark" aria-hidden="true"></span></button>'
              f'<figcaption><span class="take">Take {job[-1]}</span> <span class="how">{esc(take)}</span>'
              f'<button type="button" class="zoom" data-src="{src}" aria-label="View full size">Full size</button></figcaption></figure>')
        rows_html.append(f'<div class="subject"><h3>{esc(sname)}</h3><div class="takes">{"".join(figs)}</div></div>')
    flags = ''.join(f'<li>{inline(f)}</li>' for f in z['flags'])
    body = (f'<details class="desc"><summary>Read the full zone description</summary>'
            f'<div class="desc-body">{z["body"]}</div></details>') if z['body'] else ''
    sections.append(f'''
<section class="zone" id="z-{z["slug"]}" data-zone="{z["slug"]}">
  <header class="zhead">
    <div class="ztitle"><h2>{esc(z["name"])}</h2><p class="status" data-status="{z["slug"]}">No picks yet</p></div>
    <p class="lede">{inline(z["lede"])}</p>
    {f'<div class="flags"><h4>Choices to check</h4><ul>{flags}</ul></div>' if flags else ''}
    {body}
  </header>
  {''.join(rows_html)}
  <label class="note"><span>Notes for this zone (art direction, description changes)</span>
    <textarea id="note-{z["slug"]}" data-note="{z["slug"]}" rows="3" placeholder="e.g. warmer light, drop the raiders, keep take 3's camera"></textarea></label>
</section>''')

zone_ids = json.dumps([z['slug'] for z in zones])
page = open(f'{OUT}/template.html').read()
page = page.replace('%%NAV%%', ''.join(nav)).replace('%%SECTIONS%%', ''.join(sections)).replace('%%ZONES%%', zone_ids)
open(f'{OUT}/index.html', 'w').write(page)
print('zones', len(zones), 'images', sum(len(c) for z in zones for _, _, c in z['rows']))
