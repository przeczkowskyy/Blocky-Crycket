import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

const API_PORT = Number(process.env.STUDIO_PORT ?? 4310);

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: { '/api': `http://127.0.0.1:${API_PORT}` },
  },
  build: { outDir: 'dist', chunkSizeWarningLimit: 4000 },
});
