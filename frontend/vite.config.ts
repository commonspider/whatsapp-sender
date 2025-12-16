import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

// https://vite.dev/config/
export default defineConfig({
  plugins: [svelte()],
  build: {
    outDir: "../build",
    emptyOutDir: true,
    minify: false,
    rollupOptions: {
      input: "src/inject.ts",
      output: {
        entryFileNames: "[name].js",
      },
    },
  },
});
