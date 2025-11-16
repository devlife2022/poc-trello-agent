import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Set base path for GitHub Pages deployment
  // Update this to match your repository name
  base: process.env.NODE_ENV === 'production' ? '/poc-trello-agent/' : '/',
})
