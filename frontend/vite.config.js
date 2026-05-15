import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  if (mode === "production" && !env.VITE_API_URL) {
    throw new Error("VITE_API_URL must be set for production frontend builds.");
  }

  return {
    plugins: [react()],
    server: {
      port: 3000,
      strictPort: true,
      proxy: {
        "/api": {
          target: "http://localhost:8011",
          changeOrigin: true
        }
      }
    }
  };
});
