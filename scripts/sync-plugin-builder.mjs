import { copyFile, stat } from "node:fs/promises";
import { resolve } from "node:path";

const source = resolve("dist/index.html");
const destination = resolve(
  "plugins/icon-design/skills/icon-design/assets/icon-brief-builder.html"
);

const sourceStats = await stat(source);
if (!sourceStats.isFile()) {
  throw new Error(`Built brief builder not found: ${source}`);
}

await copyFile(source, destination);
console.log(`Synced plugin brief builder: ${destination}`);
