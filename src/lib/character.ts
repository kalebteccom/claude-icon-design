export const AXIS_NAMES = [
  "complexity",
  "geometry",
  "energy",
  "tone",
  "density",
  "novelty"
] as const;

export type AxisName = (typeof AXIS_NAMES)[number];
export type CharacterAxes = Record<AxisName, number>;

export const AXIS_META: Record<
  AxisName,
  { label: string; low: string; high: string; words: readonly string[] }
> = {
  complexity: {
    label: "Complexity",
    low: "Minimal",
    high: "Intricate",
    words: ["minimal", "spare", "balanced", "detailed", "intricate"]
  },
  geometry: {
    label: "Geometry",
    low: "Organic",
    high: "Strict",
    words: ["organic", "soft", "balanced", "geometric", "strictly geometric"]
  },
  energy: {
    label: "Energy",
    low: "Still",
    high: "Dynamic",
    words: ["still", "calm", "steady", "active", "dynamic"]
  },
  tone: {
    label: "Playfulness",
    low: "Serious",
    high: "Playful",
    words: ["serious", "restrained", "balanced", "friendly", "playful"]
  },
  density: {
    label: "Density",
    low: "Open",
    high: "Dense",
    words: ["very open", "open", "balanced", "compact", "dense"]
  },
  novelty: {
    label: "Novelty",
    low: "Familiar",
    high: "Experimental",
    words: ["familiar", "recognizable", "balanced", "distinctive", "experimental"]
  }
};

export const DEFAULT_AXES: CharacterAxes = {
  complexity: 2,
  geometry: 4,
  energy: 3,
  tone: 2,
  density: 3,
  novelty: 3
};

export interface GlyphGeometry {
  rotation: number;
  cornerRadius: number;
  left: { x: number; y: number; width: number; height: number };
  right: {
    x: number;
    y: number;
    width: number;
    height: number;
    rotation: number;
    centerX: number;
    centerY: number;
  };
  bridge: { x: number; y: number; width: number; height: number; radius: number };
  notch: { x: number; y: number; radius: number; opacity: number };
  detailOne: { x: number; y: number; radius: number; opacity: number };
  detailTwo: { x: number; y: number; width: number; height: number; radius: number; opacity: number };
}

const round = (value: number) => Number(value.toFixed(2));
const normalize = (value: number) => (Math.min(5, Math.max(1, value)) - 1) / 4;

export function glyphGeometry(axes: CharacterAxes): GlyphGeometry {
  const complexity = normalize(axes.complexity);
  const geometry = normalize(axes.geometry);
  const energy = normalize(axes.energy);
  const playfulness = normalize(axes.tone);
  const density = normalize(axes.density);
  const novelty = normalize(axes.novelty);

  const moduleWidth = 11.5 + density * 3;
  const moduleHeight = 22 + complexity * 7;
  const spread = 11.5 + (1 - density) * 4;
  const bounce = playfulness * 5;
  const leftCenterX = 32 - spread;
  const rightCenterX = 32 + spread;
  const leftY = 32 - moduleHeight / 2 + bounce / 2;
  const rightY = 32 - moduleHeight / 2 - bounce / 2;
  const leftX = leftCenterX - moduleWidth / 2;
  const rightX = rightCenterX - moduleWidth / 2;
  const bridgeX = leftX + moduleWidth - 1;
  const bridgeRight = rightX + 1;
  const bridgeHeight = 4 + density * 4;
  const cornerRadius = 2 + (1 - geometry) * 8;

  return {
    rotation: round(-energy * 11),
    cornerRadius: round(cornerRadius),
    left: {
      x: round(leftX),
      y: round(leftY),
      width: round(moduleWidth),
      height: round(moduleHeight)
    },
    right: {
      x: round(rightX),
      y: round(rightY),
      width: round(moduleWidth),
      height: round(moduleHeight),
      rotation: round(novelty * 10),
      centerX: round(rightCenterX),
      centerY: round(rightY + moduleHeight / 2)
    },
    bridge: {
      x: round(bridgeX),
      y: round(32 - bridgeHeight / 2),
      width: round(Math.max(2, bridgeRight - bridgeX)),
      height: round(bridgeHeight),
      radius: round(Math.min(cornerRadius / 2, bridgeHeight / 2))
    },
    notch: {
      x: round(rightCenterX + novelty * 2),
      y: round(32 - bounce / 2),
      radius: round(1.25 + novelty * 4),
      opacity: 1
    },
    detailOne: {
      x: round(leftCenterX),
      y: round(leftY + moduleHeight / 2 - 4),
      radius: round(1.1 + complexity * 1.5),
      opacity: round(Math.min(1, Math.max(0, (complexity - 0.25) / 0.5)))
    },
    detailTwo: {
      x: round(leftCenterX - (2 + complexity * 2) / 2),
      y: round(leftY + moduleHeight / 2 + 3),
      width: round(2 + complexity * 2),
      height: round(1.6 + complexity * 1.4),
      radius: round((1 - geometry) * 1.5),
      opacity: round(Math.min(1, Math.max(0, (complexity - 0.5) / 0.25)))
    }
  };
}

export function axesFromBits(bits: readonly number[], low = 2, high = 4): CharacterAxes {
  if (bits.length !== AXIS_NAMES.length) {
    throw new Error(`Expected ${AXIS_NAMES.length} character bits`);
  }
  return Object.fromEntries(
    AXIS_NAMES.map((name, index) => [name, bits[index] ? high : low])
  ) as CharacterAxes;
}

export function permutationBits(index: number): number[] {
  if (!Number.isInteger(index) || index < 0 || index >= 64) {
    throw new Error("Character permutation index must be from 0 to 63");
  }
  return AXIS_NAMES.map((_, bitIndex) => (index >> (5 - bitIndex)) & 1);
}

export function quantizedBits(axes: CharacterAxes): number[] {
  return AXIS_NAMES.map((name) => (axes[name] <= 2 ? 0 : 1));
}

export function permutationLabel(bits: readonly number[]): string {
  return AXIS_NAMES.map((name, index) =>
    AXIS_META[name].words[bits[index] ? 3 : 1]
  ).join(" · ");
}

export function axisSummary(axes: CharacterAxes): string {
  return AXIS_NAMES.map((name) => {
    const score = axes[name];
    return `${name} ${score}/5 (${AXIS_META[name].words[score - 1]})`;
  }).join("; ");
}

export function characterName(axes: CharacterAxes): string {
  const strongest = [...AXIS_NAMES]
    .sort((a, b) => Math.abs(axes[b] - 3) - Math.abs(axes[a] - 3))
    .slice(0, 2);
  return strongest.map((name) => AXIS_META[name].words[axes[name] - 1]).join(" + ");
}
