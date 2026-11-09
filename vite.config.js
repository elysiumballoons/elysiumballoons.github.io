import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages serves the site under /elysiumballons/. Set VITE_BASE=/ for a root domain (Netlify/Vercel).
export default defineConfig({
  base: process.env.VITE_BASE || "/",
  plugins: [react()],
  build: { chunkSizeWarningLimit: 4000 },
});
