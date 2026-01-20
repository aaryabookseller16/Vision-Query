import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/**
 * vite.config.js
 *
 * Purpose:
 * - Configure the Vite dev server for the VisionQuery frontend.
 * - Add a development-time proxy so frontend code can call the backend
 *   without hardcoding localhost:8000 or dealing with CORS.
 *
 * How it works:
 * - Any request starting with /api will be forwarded to the FastAPI backend.
 * - Example:
 *     fetch("/api/search")  -->  http://localhost:8000/search
 *
 * This setup is for local development only.
 */
export default defineConfig({
  plugins: [react()],

  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
