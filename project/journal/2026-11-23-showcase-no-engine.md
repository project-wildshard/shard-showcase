# Showcase reads no engine

> Written by: Claude (lane opus-prune1)

SHARD-COMPAT SI5 and SI8: the showcase holds no shard source, so its Vitest config drops the engine's Rapier aliases,
`assert-store-layout.mjs` takes the kit's copy (no engine app-builder probe), and the direct `@wildshard/engine`
dev dependency goes. The census reads 0 for every shard repo.
