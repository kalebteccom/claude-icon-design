/// <reference types="vitest/config" />

import { defineConfig } from "vite";
import solid from "vite-plugin-solid";

export default defineConfig({
  plugins: [solid()],
  resolve: {
    conditions: ["browser"]
  },
  test: {
    environment: "node"
  }
});
