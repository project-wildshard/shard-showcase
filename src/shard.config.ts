import { showcase } from './generators/shard'

/** The build entry: the scene shard `generators/shard.ts` defines. */
export const generate: typeof showcase = showcase
// oxlint-disable-next-line import/no-default-export -- The author CLI executes this project entry.
export default generate
