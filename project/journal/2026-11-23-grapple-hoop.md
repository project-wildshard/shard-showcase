# West grapple course: shared hoop and placement study

W7a calls for five hooks. The W08 art and existing post already cover the
geometry needed for a shared hoop; no new tower, zip house or cable is needed
in this pass. Extracted the exact cyan hoop and recessed mint channel from
`wsc-prop-034-grapple-hook-post.glb`. Kept the donor unmodified.

- Centered the extracted sample at the ring center, originally glTF
  `(0, 2.557, 0)`. Face convention: glTF +Z; aperture lies in glTF XY.
- Reimport matched all 2,112 material-tagged triangles after translating
  the donor to the new origin. Bounds are .736 m wide and tall, 89.6 mm deep;
  new GLB is 40,196 bytes. Post and roof-mount illustration are studio
  dressing, not part of the export. The roof mount puts the hoop center
  1.25 m above the deck.
- The earlier shared-roof art script has an ornamental center torus at
  world `(-206,19.7,-104)`; it was not a native hook. An alternate
  study position on the north side of the roof has ring center at
  `(-198,19.25,-92)`. Its horizontal origin is 1.58 m inside the
  source roof perimeter. World coordinates are X/Y/Z, Y up.
- Pole 2 to the old ring center is 51.05 m; to the proposed roof ring is
  37.02 m. The historical mast and tower ring proxies are 41.03 m apart.
  The default limit is 38 m **from player eye to hook**, not from one ring
  to the next. The W7a plan's advertised distances are not proven by this
  study. Before placing native hooks, measure usable departure surfaces,
  takeoff-eye positions and line of sight. No upgrade, collision, camera
  acquisition or traversal proof. W7b zip attachment coordinates unchanged.

Rebuild from this repository root with Blender 4.3.2 and Python:

```sh
S=scripts/blender/showcase-studies
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python "$S/grapple_hoop.py" -- /tmp/grapple
python "$S/grapple_route_svg.py" /tmp/grapple/w7a-hoop-placement-study.json \
  /tmp/grapple/nov23-grapple-center-spans.svg
```

`project/layouts/w7a-hoop-placement-study.json` records provenance, reference
points and W7b endpoints. The chart is generated from the same values.
