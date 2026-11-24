# Titan bowl: the view from 30 m

Reimport the current bowl unchanged and check the far-stand horizon
flagged by E12h. No actor, cutscene asset, or native scene is added.
The 6 m and 15 m guides are measurement marks, not actor or pile art.
The camera looking straight down at (0,64) sees a sector seam; moving
3.4 m sideways places the view above a real terrace, with 11.25 m of
clearance. Neither pin is a validated in-game camera path.

| Study | Vertical / horizontal FOV | Rays that miss exported bowl |
| --- | --- | --- |
| North portrait | 55° / 26.93° | 29.51% |
| Angled portrait | 55° / 26.93° | 30.69% |
| North landscape review | 55° / 75.57° | 26.72% |
| Floor-first portrait | 45° / 21.57° | 7.93% |

Each result samples 7,200 camera rays against only the donor mesh, not
pixel colors. The top quarter of both 55° portraits has no bowl hits.
The checkpoint mouth is in sight; the deeper panel is obscured.
Choose the 45° floor-first framing for the center shot if the backdrop
is not built. Retain the wider review as the scenery target; a painted
world or plane in Blender is not an exported chamber. The guides'
visibility does not establish clearance for the eventual moving Titan.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/titan_stands_review.py \
  -- /tmp/titan-stands
```

Set WSC_STANDS_RAYS_ONLY=1 for the numerical proof without rendering.
