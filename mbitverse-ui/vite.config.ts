import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/full_pipeline": { target: "http://localhost:8000", changeOrigin: true },
      "/agents": { target: "http://localhost:8000", changeOrigin: true },
      "/reaction": { target: "http://localhost:8000", changeOrigin: true },
    },
  },
});
