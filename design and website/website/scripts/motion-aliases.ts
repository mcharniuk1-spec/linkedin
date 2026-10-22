import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
// Resolve the pinned packages' official CommonJS entries. This also avoids
// reading hundreds of small ES modules from evicted/mounted source trees.
export const motionAliases = [
  { find: /^motion\/react$/, replacement: require.resolve('motion/react') },
  { find: /^framer-motion$/, replacement: require.resolve('framer-motion') },
  { find: /^motion-dom$/, replacement: require.resolve('motion-dom') },
  { find: /^motion-utils$/, replacement: require.resolve('motion-utils') },
];
