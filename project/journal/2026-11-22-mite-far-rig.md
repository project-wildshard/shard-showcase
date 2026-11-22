# Crate Mite far rig: 138 triangles

The E1b far mesh is a second output from the editable Mite recipe. It keeps
the orange chamfered crate, cyan lens and four moving legs, but fuses the
collar, strut and foot into one rigid wedge per leg. It stays under the
150-triangle far budget without making a second animation source.

Two clean Blender 4.3.2 builds matched byte for byte. The existing 386-triangle
phone rig also rebuilt byte for byte. The 104,420-byte far GLB loads with the
same seven named joints and eleven clips; the Three loader checks the weights,
attack crouch/lift, turning, closed eye and grounding of death debris for both.
All four standalone combat tests passed. The alternate export is not wired
to an automatic distance switch in either runtime.
