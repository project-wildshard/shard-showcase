# West Town: Tinker Rook and the street counter

WSC-ACTOR-018 is a rigged art study. The orange vest, pocketed chestnut apron, metal limb shells and amber visor follow the WSC-ACTOR-018 provisional turnaround. The round-11 W04 street image motivated the awning and keeper composition. UPGRADES and BENCH are W2b, not implemented here.

The actor is 150,112 bytes and 4,692 triangles, one skinned primitive on the common 21-joint W1a rig and color atlas. The GLB requires EXT_meshopt_compression. The 3 s Idle_Studio source exports as GLB clip Animation. Reimport checked joint count, one-material skin, pose motion, near-zero rest sole height and loop return. This is not native NPC admission, walking, shop routing or trade behavior.

WSC-SCENE-002 is an open-air frontage composition. The shallow facade is still closed. The counter comes from the existing shop kit, but stands on the street; there is no new room. Awning, wrench, lantern, cargo crate, paving and flanking street bay use unchanged donor meshes. The JSON records donor hashes and artist placements, not native map anchors. No duplicate storefront or kit export.

From the root, use a temporary directory outside the checkout:

    out="$(mktemp -d)"
    WSC_TOWN_ROOK=1 blender -b -t 6 --factory-startup --python-exit-code 1 --python scripts/blender/showcase-studies/town_bots.py -- "$out"
    node scripts/blender/showcase-studies/surveyor_pack.mjs node_modules "$out" tinker-rook
    blender -b -t 6 --factory-startup --python-exit-code 1 --python scripts/blender/showcase-studies/rook_counter.py -- "$out"

The packer also emits a temporary decoded copy for Blender. Keep only the packed asset in the art tree. Source and placement JSON replace a duplicate blend file or whole-scene GLB.
