import declared from './generators/product'

/** The build entry: the bare shard file `generators/product.ts` declares. */
export const product: typeof declared = declared
// oxlint-disable-next-line import/no-default-export -- The author CLI loads this build entry.
export default product
