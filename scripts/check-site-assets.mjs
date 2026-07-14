import { access, readFile } from "node:fs/promises";
import { resolve } from "node:path";
import sharp from "sharp";

const requireText = (content, fragment, filename) => {
  if (!content.includes(fragment)) {
    throw new Error(`${filename} is missing ${fragment}`);
  }
};

const html = await readFile(resolve("index.html"), "utf8");
for (const fragment of [
  '<link rel="canonical" href="https://icons.kalebtec.com/"',
  'property="og:image" content="https://icons.kalebtec.com/og-card.png"',
  'name="twitter:card" content="summary_large_image"',
  'name="supported-color-schemes" content="light dark"',
  'max-image-preview:large',
  '<script type="application/ld+json">',
  '<noscript>',
  '<link rel="manifest" href="/site.webmanifest"',
  '<link rel="sitemap" type="application/xml" href="/sitemap.xml"'
]) {
  requireText(html, fragment, "index.html");
}

const jsonLdMatch = html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/);
if (!jsonLdMatch) throw new Error("index.html has no JSON-LD block");
const jsonLd = JSON.parse(jsonLdMatch[1]);
if (jsonLd["@type"] !== "WebApplication") throw new Error("JSON-LD type must be WebApplication");
if (jsonLd.inLanguage !== "en") throw new Error("JSON-LD language must match the English document");

const manifest = JSON.parse(await readFile(resolve("public/site.webmanifest"), "utf8"));
if (manifest.start_url !== "/" || manifest.icons.length < 3) {
  throw new Error("site.webmanifest is missing its start URL or icons");
}
if (!manifest.icons.some((icon) => icon.type === "image/svg+xml" && icon.purpose.includes("monochrome"))) {
  throw new Error("site.webmanifest must include the adaptive standalone SVG mark");
}
if (manifest.icons.some((icon) => icon.purpose.includes("maskable"))) {
  throw new Error("site.webmanifest must not restore the background-tile icon");
}

const robots = await readFile(resolve("public/robots.txt"), "utf8");
requireText(robots, "Sitemap: https://icons.kalebtec.com/sitemap.xml", "robots.txt");

const sitemap = await readFile(resolve("public/sitemap.xml"), "utf8");
requireText(sitemap, "<loc>https://icons.kalebtec.com/</loc>", "sitemap.xml");

for (const [filename, width, height] of [
  ["og-card.png", 1200, 630],
  ["favicon-16x16.png", 16, 16],
  ["favicon-32x32.png", 32, 32],
  ["favicon-48x48.png", 48, 48],
  ["apple-touch-icon.png", 180, 180],
  ["icon-192.png", 192, 192],
  ["icon-512.png", 512, 512]
]) {
  const path = resolve("public", filename);
  await access(path);
  const metadata = await sharp(path).metadata();
  if (metadata.width !== width || metadata.height !== height) {
    throw new Error(`${filename} must be ${width}x${height}`);
  }
}

const faviconSvg = await readFile(resolve("public/favicon.svg"), "utf8");
if (faviconSvg.includes("<rect") || !faviconSvg.includes("prefers-color-scheme: dark")) {
  throw new Error("favicon.svg must use the adaptive standalone Kalebtec mark");
}

for (const filename of ["apple-touch-icon.png", "icon-192.png", "icon-512.png"]) {
  const { data } = await sharp(resolve("public", filename))
    .ensureAlpha()
    .raw()
    .toBuffer({ resolveWithObject: true });
  if (data[3] !== 0) throw new Error(`${filename} must keep a transparent background`);
}

const faviconIco = await readFile(resolve("public/favicon.ico"));
if (faviconIco.readUInt16LE(2) !== 1 || faviconIco.readUInt16LE(4) !== 3) {
  throw new Error("favicon.ico must contain the 16, 32, and 48 px icons");
}

console.log("SEO metadata and generated site assets are valid.");
