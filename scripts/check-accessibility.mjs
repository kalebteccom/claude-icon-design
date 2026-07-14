import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

const css = await readFile(resolve("src/styles.css"), "utf8");

function variablesFor(pattern, name) {
  const match = css.match(pattern);
  if (!match) throw new Error(`Could not find the ${name} theme tokens`);
  return Object.fromEntries(
    [...match[1].matchAll(/--([\w-]+):\s*(#[0-9a-fA-F]{6})\s*;/g)].map((entry) => [entry[1], entry[2]])
  );
}

function luminance(hex) {
  const channels = hex.match(/[0-9a-f]{2}/gi).map((value) => Number.parseInt(value, 16) / 255);
  const linear = channels.map((value) => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4);
  return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
}

function contrast(first, second) {
  const a = luminance(first);
  const b = luminance(second);
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
}

function requireContrast(theme, foreground, background, minimum) {
  const ratio = contrast(theme[foreground], theme[background]);
  if (ratio < minimum) {
    throw new Error(`${foreground} on ${background} is ${ratio.toFixed(2)}:1; expected at least ${minimum}:1`);
  }
}

const themes = {
  light: variablesFor(/^:root\s*\{([\s\S]*?)\n\}/m, "light"),
  dark: variablesFor(/:root\[data-theme="dark"\]\s*\{([\s\S]*?)\n\}/m, "dark")
};

for (const [name, theme] of Object.entries(themes)) {
  for (const background of ["page", "surface", "surface-strong", "surface-muted", "accent-soft"]) {
    requireContrast(theme, "ink", background, 4.5);
    requireContrast(theme, "muted", background, 4.5);
  }
  for (const background of ["page", "surface", "surface-muted"]) {
    requireContrast(theme, "accent", background, 4.5);
  }
  requireContrast(theme, "accent-ink", "accent-fill", 4.5);
  for (const background of ["page", "surface", "surface-strong", "surface-muted", "accent-soft"]) {
    requireContrast(theme, "control-line", background, 3);
    requireContrast(theme, "focus", background, 3);
  }
  console.log(`${name} theme contrast checks passed.`);
}
