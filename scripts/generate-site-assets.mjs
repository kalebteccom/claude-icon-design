import { copyFile, mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import sharp from "sharp";

const cardSource = resolve("assets/og-card.svg");
const faviconSource = resolve(".github/icon-design-mark.svg");
const publicDirectory = resolve("public");
const card = await readFile(cardSource);
const favicon = await readFile(faviconSource);

await mkdir(publicDirectory, { recursive: true });

await sharp(card, { density: 96 })
  .resize(1200, 630, { fit: "fill" })
  .png({ compressionLevel: 9, palette: true, quality: 100 })
  .toFile(resolve(publicDirectory, "og-card.png"));

const faviconPngs = [];
for (const size of [16, 32, 48]) {
  const rendered = await sharp(favicon, { density: 384 })
    .resize(size, size, { fit: "fill" })
    .png({ compressionLevel: 9 })
    .toBuffer();
  faviconPngs.push({ size, rendered });
  await writeFile(resolve(publicDirectory, `favicon-${size}x${size}.png`), rendered);
}

await sharp(favicon, { density: 384 })
  .resize(180, 180, { fit: "fill" })
  .png({ compressionLevel: 9 })
  .toFile(resolve(publicDirectory, "apple-touch-icon.png"));

const icoHeader = Buffer.alloc(6 + faviconPngs.length * 16);
icoHeader.writeUInt16LE(0, 0);
icoHeader.writeUInt16LE(1, 2);
icoHeader.writeUInt16LE(faviconPngs.length, 4);
let icoOffset = icoHeader.length;
faviconPngs.forEach(({ size, rendered }, index) => {
  const entry = 6 + index * 16;
  icoHeader.writeUInt8(size, entry);
  icoHeader.writeUInt8(size, entry + 1);
  icoHeader.writeUInt8(0, entry + 2);
  icoHeader.writeUInt8(0, entry + 3);
  icoHeader.writeUInt16LE(1, entry + 4);
  icoHeader.writeUInt16LE(32, entry + 6);
  icoHeader.writeUInt32LE(rendered.length, entry + 8);
  icoHeader.writeUInt32LE(icoOffset, entry + 12);
  icoOffset += rendered.length;
});
await writeFile(
  resolve(publicDirectory, "favicon.ico"),
  Buffer.concat([icoHeader, ...faviconPngs.map(({ rendered }) => rendered)])
);

for (const [filename, size] of [
  ["icon-192.png", 192],
  ["icon-512.png", 512]
]) {
  await sharp(favicon, { density: 384 })
    .resize(size, size, { fit: "fill" })
    .png({ compressionLevel: 9 })
    .toFile(resolve(publicDirectory, filename));
}

await copyFile(faviconSource, resolve(publicDirectory, "favicon.svg"));

console.log("Generated Open Graph card, favicons, and install icons.");
