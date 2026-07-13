import { defineConfig } from "vite";
import solid from "vite-plugin-solid";
import { viteSingleFile } from "vite-plugin-singlefile";

export default defineConfig({
  base: "./",
  plugins: [solid(), viteSingleFile()],
  build: {
    cssCodeSplit: false,
    sourcemap: false,
    target: "es2022"
  }
});
