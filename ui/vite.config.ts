import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
export default defineConfig({
  plugins: [vue()],
  base: '/ui/',
  build: {
    outDir: '../workbench/web',
    emptyOutDir: true,
    cssCodeSplit: false,
    rollupOptions: {
      output: {
        entryFileNames: 'app.js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name][extname]',
        inlineDynamicImports: true,
      },
    },
  },
  server: {
    proxy: Object.fromEntries(
      [
        '/projects',
        '/runs',
        '/models',
        '/settings',
        '/catalog',
        '/templates',
        '/health',
        '/ready',
      ].map((p) => [p, 'http://127.0.0.1:8000']),
    ),
  },
  test: { environment: 'jsdom', include: ['tests/**/*.test.ts'], restoreMocks: true },
})
