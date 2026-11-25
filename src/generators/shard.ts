// The shard: one scene module (world.ts). `wildshard build` runs this as the
// shard's generator; `wildshard watch` streams its parts to a running page.
import { defineShard } from '@wildshard/sdk/scene/shard'

import { buildWorld } from './world'

export const showcase = defineShard(
  {
    slug: 'shard-showcase',
    name: 'shard-showcase',
    author: 'Local author',
    revision: 1,
    seed: 1,
  },
  buildWorld,
)
