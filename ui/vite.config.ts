import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

export default defineConfig({
  base: '/ui/',
  plugins: [react()],
  server: {
    proxy: {
      '/chat': {
        target: 'http://api:8000',
        changeOrigin: true,
        // Handles /chat and any /chat/*
      },
      '/openscad_playground': {
        target: 'http://api:8000',
        changeOrigin: true,
        // Handles /openscad_playground and any /openscad_playground/*
      }
    },
  },
});
