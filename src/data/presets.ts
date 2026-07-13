import type { CharacterAxes } from "../lib/character";
import type { StyleId } from "../components/StyleSpecimen";

export interface CharacterPreset {
  id: string;
  name: string;
  note: string;
  pairsWith: readonly StyleId[];
  axes: CharacterAxes;
}

export const CHARACTER_PRESETS: readonly CharacterPreset[] = [
  {
    id: "quiet-precision",
    name: "Quiet precision",
    note: "Calm, spare, and disciplined. Useful when trust should come from restraint.",
    pairsWith: ["geometric", "monoline"],
    axes: { complexity: 1, geometry: 5, energy: 1, tone: 1, density: 2, novelty: 2 }
  },
  {
    id: "friendly-utility",
    name: "Friendly utility",
    note: "Warm without becoming childish; clear enough for everyday product use.",
    pairsWith: ["humanist", "solid glyph"],
    axes: { complexity: 2, geometry: 2, energy: 3, tone: 4, density: 3, novelty: 2 }
  },
  {
    id: "technical-momentum",
    name: "Technical momentum",
    note: "Measured construction with forward motion and a distinctive engineered edge.",
    pairsWith: ["technical", "modular"],
    axes: { complexity: 3, geometry: 5, energy: 5, tone: 1, density: 3, novelty: 4 }
  },
  {
    id: "bold-signal",
    name: "Bold signal",
    note: "Compact, confident, and legible when the icon has very little room.",
    pairsWith: ["solid glyph", "negative space"],
    axes: { complexity: 2, geometry: 4, energy: 4, tone: 2, density: 5, novelty: 3 }
  },
  {
    id: "playful-system",
    name: "Playful system",
    note: "Lively modular rhythm with enough structure to extend into an icon family.",
    pairsWith: ["modular", "organic"],
    axes: { complexity: 3, geometry: 3, energy: 4, tone: 5, density: 3, novelty: 4 }
  },
  {
    id: "unusual-emblem",
    name: "Unusual emblem",
    note: "Richer and more ownable, suited to a mark that can carry a stronger story.",
    pairsWith: ["emblem", "dimensional"],
    axes: { complexity: 4, geometry: 4, energy: 3, tone: 3, density: 4, novelty: 5 }
  }
];

export function presetById(id: string | null | undefined): CharacterPreset | undefined {
  return CHARACTER_PRESETS.find((preset) => preset.id === id);
}
