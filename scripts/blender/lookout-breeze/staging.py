"""Reimport and stage the original W11 trail, with per-clump preview phases."""
import json
import math

import bpy

from build import KEYS, SPEC, TARGETS, weights


def sampled_weights(u):
    # Reproduce LINEAR glTF sampling, not a smoother function than actually ships.
    k = (u % 1) * (KEYS-1)
    i = min(KEYS-2, math.floor(k))
    a, b = weights(i/(KEYS-1)), weights(((i+1)%(KEYS-1))/(KEYS-1))
    return [l+(r-l)*(k-i) for l, r in zip(a, b)]


def render_breeze(scene, out, slots, camera):
    assert len(slots) == 15
    checks = []
    for i, (name, ob, xyz, yaw, scale) in enumerate(slots):
        basis, *targets = ob.data.shape_keys.key_blocks
        assert [k.name for k in targets] == list(TARGETS)
        _, aw, cw, period = SPEC[name]
        roots = [j for j, pt in enumerate(basis.data) if pt.co.z <= .045]
        assert roots and all((t.data[j].co-basis.data[j].co).length == 0 for t in targets for j in roots)
        rest = min(abs((ob.matrix_world @ pt.co).x)-1 for pt in basis.data)
        margin = rest-scale*math.hypot(aw,cw)
        assert margin > .015, (name, margin)
        checks.append(dict(name=name, xyz=xyz, yaw=yaw, scale=scale, phase_cycles=(i*7%19)/19,
                           pinned_vertices=len(roots), mathematical_clearance_m=round(margin,6)))
    (out/"lookout-breeze-staging.json").write_text(json.dumps(checks,indent=2)+"\n")
    scene.render.engine="CYCLES"
    scene.cycles.samples=22
    scene.cycles.seed=29
    scene.cycles.use_animated_seed=False
    scene.cycles.use_denoising=False
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.view_settings.view_transform="AgX"
    scene.view_settings.look="AgX - Medium High Contrast"

    def pose(t):
        for row, (name, ob, _, _, _) in zip(checks,slots):
            vals = ([0]*4 if t is None else sampled_weights(t/SPEC[name][3]+row["phase_cycles"]))
            for block, v in zip(list(ob.data.shape_keys.key_blocks)[1:],vals):
                block.value=v
        bpy.context.view_layer.update()

    def shot(name, x, y, t):
        pose(t)
        scene.render.resolution_x,scene.render.resolution_y=x,y
        scene.render.filepath=str(out/f"{name}.png")
        bpy.ops.render.render(write_still=True)

    shot("w11-breeze-trail",1280,850,1.2)
    camera((-1.56,-2.23,.61),(-1.59,-.80,.19),lens=45)
    shot("w11-breeze-detail-rest",900,690,None)
    shot("w11-breeze-detail-moving",900,690,1.2)
