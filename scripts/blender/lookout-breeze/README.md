# W11 — optional lookout breeze
Two opt-in variants of the original fern and folded verge grass, not replacements.
The static mesh, colors, normals, triangle indices and material remain identical.
The optional clips return exactly to rest at both ends; the basal 45 mm is pinned
and tips move at most 32 mm (fern) or 26 mm (verge). The two different loop
durations and per-instance start offsets avoid identical motion in the review.
Reuse the static GLBs where movement is unnecessary. This adds no runtime weather,
terrain placement, collision, or measured GPU budget.

```sh
out=/tmp/lookout-breeze
python scripts/blender/lookout-breeze/build.py "$out"
WSC_LOOKOUT_BREEZE_DIR="$out" blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/lookout_understory.py -- "$out"
node scripts/blender/lookout-breeze/check.mjs "$out"
magick "$out/w11-breeze-trail.png" -strip -quality 86 -define webp:method=6 "$out/nov25-w11-breeze-trail.webp"
magick "$out/w11-breeze-detail-rest.png" "$out/w11-breeze-detail-moving.png" \
  +append -resize 1400x -strip -quality 87 -define webp:method=6 "$out/nov25-w11-breeze-detail.webp"
```

The Node check uses the local Three dependency. For three.js, play the clip on
the loaded scene's AnimationMixer, creating a mixer per independently phased
clump. The four normal and position morphs use ordinary glTF, without extensions.
The headless check tests every vertex at every authored key in all 15 trail
positions. Between keys, vertex X interpolates linearly: the smallest recorded
gap to the 2 m path strip, about 71 mm, also bounds the in-between motion.
No GPU timing or check of other vegetation, rocks, and layout collision is implied.
