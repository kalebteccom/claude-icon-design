import { writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { For } from "solid-js";
import { renderToString } from "solid-js/web";
import { Glyph } from "../src/components/Glyph";
import { CHARACTER_PRESETS } from "../src/data/presets";
import { axesFromBits, permutationBits } from "../src/lib/character";

const matrix = Array.from({ length: 64 }, (_, index) => ({
  index,
  axes: axesFromBits(permutationBits(index))
}));

function CharacterSheet() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 1160" width="960" height="1160">
      <rect width="960" height="1160" fill="#eeeae2" />
      <text x="64" y="58" fill="#171815" font-family="Arial, sans-serif" font-size="28" font-weight="700">Character reference</text>
      <text x="64" y="86" fill="#6b6c66" font-family="Arial, sans-serif" font-size="14">64 exact 2/4 landmarks · six guided presets</text>
      <g transform="translate(64 116)">
        <For each={matrix}>
          {(entry) => {
            const column = entry.index % 8;
            const row = Math.floor(entry.index / 8);
            return (
              <g transform={`translate(${column * 104} ${row * 104})`}>
                <rect width="92" height="92" rx="11" fill="#fbfaf7" stroke="#d7d2c7" />
                <Glyph axes={entry.axes} id={`sheet-matrix-${entry.index}`} class="sheet-glyph" />
                <text x="8" y="84" fill="#777870" font-family="Arial, sans-serif" font-size="9">{entry.index + 1}</text>
              </g>
            );
          }}
        </For>
      </g>
      <text x="64" y="990" fill="#171815" font-family="Arial, sans-serif" font-size="18" font-weight="700">Guided presets</text>
      <g transform="translate(64 1014)">
        <For each={CHARACTER_PRESETS}>
          {(preset, index) => (
            <g transform={`translate(${index() * 139} 0)`}>
              <rect width="126" height="110" rx="11" fill="#fbfaf7" stroke="#d7d2c7" />
              <Glyph axes={preset.axes} id={`sheet-preset-${preset.id}`} class="preset-glyph" />
              <text x="63" y="98" text-anchor="middle" fill="#4f504b" font-family="Arial, sans-serif" font-size="9">{preset.name}</text>
            </g>
          )}
        </For>
      </g>
      <style>{`.sheet-glyph { width: 68px; height: 68px; x: 12px; y: 9px; color: #171815; } .preset-glyph { width: 72px; height: 72px; x: 27px; y: 8px; color: #171815; }`}</style>
    </svg>
  );
}

const output = resolve(process.argv[2] || "character-reference.svg");
await writeFile(output, `<?xml version="1.0" encoding="UTF-8"?>\n${renderToString(() => <CharacterSheet />)}\n`);
console.log(`Rendered character reference: ${output}`);
