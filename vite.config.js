import { realpathSync } from 'node:fs';
import { defineConfig } from 'vite';

const runtimeRoot = process.cwd();
const resolvedRoot = realpathSync.native(runtimeRoot);

export default defineConfig({
  root: resolvedRoot,
  server: {
    fs: {
      allow: [runtimeRoot, resolvedRoot]
    }
  },
  build: {
    chunkSizeWarningLimit: 700
  }
});
