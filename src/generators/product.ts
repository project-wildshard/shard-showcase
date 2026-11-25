import { emptyShardfile } from '@wildshard/sdk/author'

import { IDENTITY } from './card'

/** Build-only declaration; the CLI emits its platform sections as JSON. */
const WORLD = emptyShardfile(IDENTITY)
// oxlint-disable-next-line import/no-default-export -- The documented build entry imports this declaration.
export default WORLD
