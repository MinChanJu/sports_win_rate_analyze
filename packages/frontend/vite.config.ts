import { defineConfig } from "vite";
import svgr from "vite-plugin-svgr";
import tsconfigPaths from "vite-tsconfig-paths";

import react from "@vitejs/plugin-react-swc";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), svgr(), tsconfigPaths()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          "react-vendor": ["react", "react-dom"],
          router: ["react-router-dom"],
          query: ["@tanstack/react-query"],
          charts: ["recharts", "d3"],
        },
      },
    },
    chunkSizeWarningLimit: 600,
    sourcemap: false,
    minify: "esbuild",
  },
});
