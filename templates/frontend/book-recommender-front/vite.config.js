// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 8080,
    clearScreen: false,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8005',
        changeOrigin: true,
        // ws: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
