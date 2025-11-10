import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import fg from "fast-glob";
import path from "node:path";
import tailwindcss from "@tailwindcss/vite";

function buildInputs() {
  const files = fg.sync("src/**/index.{tsx,jsx}", { dot: false });
  return Object.fromEntries(
    files.map((f) => [path.basename(path.dirname(f)), path.resolve(f)])
  );
}

const inputs = buildInputs();

export default defineConfig({
  plugins: [tailwindcss(), react()],
  base: "/assets/",  // This ensures all assets are loaded from /assets/
  build: {
    target: "es2022",
    sourcemap: true,
    minify: "esbuild",
    outDir: "assets",
    assetsDir: ".",
    rollupOptions: {
      input: inputs,
      preserveEntrySignatures: "strict",
    },
  },
});