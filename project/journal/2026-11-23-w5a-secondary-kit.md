# W5a compact terrain kit extracts

Three standalone GLBs use the existing tracked Hover Park build, not newly drawn obstacles: the nominal 24 m bowl, four-ramp funbox and one quarter pipe. This augments WSC-KIT-003 and provides partial art evidence for WSC-SCENE-003. D7's two launch walls stay separate; WSC-PROP-030 remains a historical W07 reference, not a shipping halfpipe.

The bowl exterior is 24.9 m across, with a nominal 24 m inner lip and a 3.5 m crest. The funbox is 20 m overall with a 10 × 10 m platform at 1.8 m and four approach faces. One 6 m-run, 14 m-wide quarter source is reused at the second authored slot with 180° yaw. Its riding surface ends at 5 m plus coping, not the D7 wall cap. Source planes matched per polygon/material between quarter placements; reimport parity compared nonzero triangle surfaces/materials to the local source. Ray height samples verify selected ride-face geometry, not travel or collision. Removed only zero-area faces (64 bowl, 2 quarter); no texture assets.

From the repository root:

    tmp="$(mktemp -d)"
    blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-hover/build.py -- --output "$tmp/park"
    blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-hover/extract_secondary_kit.py -- --park-build "$tmp/park" --output "$tmp/kit"

The main park scene lives in the tracked recipe. Only small standalone components and measurements are committed here, not the temporary park scene. Studio framing shows the original relative placement for these four instances; it does not establish a playable route, collision, gameplay or measured performance.

The preview uses existing deciduous and conifer models, concrete staging and painted guidance lines outside the three exports. None of that changes the tested GLBs.
