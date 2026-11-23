# Orange East yard bay: a distance model

WSC-MODULE-020 is the orange wall with rear steel braces in the E06 family, not WSC-MODULE-023 or the Mite Yard cladding. The unchanged near GLB remains source of record. The optional distance GLB is a separate 82,780-byte single-primitive vertex-colour model (1,140 triangles, no embedded images); near is 821,832 bytes (9,436 triangles, four primitives, two images). These figures are for one source model, not a zone transfer, run-time instance cost, or measured performance.

The twelve corrugations come from the tracked donor's front and back cross-section; the largest horizontal-section error is 0.016 mm at omitted coplanar join points. The full 2.375 × 2.6715 × 0.4045 m asymmetric envelope, authored origin, ground shoes and rear-chevron silhouette are preserved. Larger edges use simple chamfers; the simplified rear bracing and paint omit detail. At 2.375 m shoe-to-shoe pitch, upper uprights are still separated by about 102 mm. No solid-wall, sealed seam, clipping, collider, runtime switch, or phone validation is implied. Exact front/rear test pairs show the same five instances, camera and lights.

From the branch root:

    blender -b -t 6 --factory-startup --python-exit-code 1 --python scripts/blender/showcase-studies/corrugated_wall_distance.py -- /tmp/mod020-proof

Set WSC_METADATA_ONLY=1 to build the GLB, reimport and write JSON without the four studio renders. The tiny Python source and identity-preserving original/dependent exports are the editable record; no extra scene archive is needed.
