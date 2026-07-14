import { STYLE_OPTIONS, type StyleId } from "../components/StyleSpecimen";
import { presetById } from "../data/presets";
import {
  AXIS_NAMES,
  DEFAULT_AXES,
  axisSummary,
  type CharacterAxes
} from "./character";

export const BRIEF_SCHEMA = "kalebtec.icon-brief.v1";
export const STORAGE_KEY = "kalebtec-icon-brief-v2";
export const LEGACY_STORAGE_KEY = "kalebtec-icon-brief-v1";

export const TARGETS = ["codex", "claude-code", "any-chatbot"] as const;
export type Target = (typeof TARGETS)[number];

export const ICON_CLASSES = [
  "brand mark",
  "app or product icon",
  "favicon",
  "system icon",
  "workflow icon",
  "monogram"
] as const;
export type IconClass = (typeof ICON_CLASSES)[number];

export const SMALLEST_SIZES = ["16 px", "20 px", "24 px", "32 px", "48 px"] as const;
export type SmallestSize = (typeof SMALLEST_SIZES)[number];

export type CharacterMode = "guided" | "custom";

export interface BriefState {
  schema: typeof BRIEF_SCHEMA;
  target: Target;
  project: string;
  iconClass: IconClass;
  purpose: string;
  audience: string;
  territories: string;
  avoid: string;
  styles: StyleId[];
  stylePreset: string | null;
  axes: CharacterAxes;
  characterMode: CharacterMode;
  characterPreset: string | null;
  smallest: SmallestSize;
  conceptCount: 20;
  backgrounds: string;
  palette: string;
  deliveryNotes: string;
  fullPackage: true;
  workflow: {
    stage: "discovery";
    round: 1;
    output: string;
    stopAfterStage: true;
  };
}

export function createDefaultBrief(): BriefState {
  return {
    schema: BRIEF_SCHEMA,
    target: "codex",
    project: "",
    iconClass: "brand mark",
    purpose: "",
    audience: "",
    territories: "",
    avoid: "",
    styles: [],
    stylePreset: null,
    axes: { ...DEFAULT_AXES },
    characterMode: "guided",
    characterPreset: null,
    smallest: "16 px",
    conceptCount: 20,
    backgrounds: "light and dark",
    palette: "",
    deliveryNotes: "",
    fullPackage: true,
    workflow: {
      stage: "discovery",
      round: 1,
      output: "numbered concept SVGs, a v2 concepts.json, and matching PNG and standalone HTML review sheets",
      stopAfterStage: true
    }
  };
}

const isString = (value: unknown): value is string => typeof value === "string";
const knownStyles = new Set<string>(STYLE_OPTIONS.map((style) => style.id));

function enumValue<T extends readonly string[]>(
  value: unknown,
  values: T,
  fallback: T[number],
  field: string
): T[number] {
  if (value === undefined) return fallback;
  if (!isString(value) || !values.includes(value as T[number])) {
    throw new Error(`${field} has an unsupported value.`);
  }
  return value as T[number];
}

function textValue(value: unknown, fallback: string, field: string): string {
  if (value === undefined) return fallback;
  if (!isString(value)) throw new Error(`${field} must be text.`);
  return value;
}

export function normalizeBrief(payload: unknown): BriefState {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    throw new Error("The brief must be a JSON object.");
  }
  const raw = payload as Record<string, unknown>;
  if (raw.schema !== BRIEF_SCHEMA) throw new Error("Unsupported brief schema.");

  const defaults = createDefaultBrief();
  const rawAxes = raw.axes;
  if (rawAxes !== undefined && (!rawAxes || typeof rawAxes !== "object" || Array.isArray(rawAxes))) {
    throw new Error("Character axes must be an object.");
  }
  const axes = { ...defaults.axes };
  if (rawAxes) {
    const values = rawAxes as Record<string, unknown>;
    for (const name of AXIS_NAMES) {
      const value = values[name];
      if (value === undefined) continue;
      if (!Number.isInteger(value) || (value as number) < 1 || (value as number) > 5) {
        throw new Error(`${name} must be an integer from 1 to 5.`);
      }
      axes[name] = value as number;
    }
  }

  let styles = defaults.styles;
  if (raw.styles !== undefined) {
    if (!Array.isArray(raw.styles) || raw.styles.length > 3) {
      throw new Error("A brief can include up to three style references.");
    }
    if (raw.styles.some((style) => !isString(style) || !knownStyles.has(style))) {
      throw new Error("The brief contains an unsupported style reference.");
    }
    styles = [...new Set(raw.styles)] as StyleId[];
  }

  const mode = enumValue(raw.characterMode, ["guided", "custom"] as const, defaults.characterMode, "characterMode");
  const requestedPreset = raw.characterPreset === null || raw.characterPreset === undefined
    ? null
    : textValue(raw.characterPreset, "", "characterPreset");
  const preset = presetById(requestedPreset);
  if (requestedPreset && !preset) throw new Error("characterPreset has an unsupported value.");
  const characterPreset = mode === "guided" && preset
    && AXIS_NAMES.every((name) => axes[name] === preset.axes[name])
    ? preset.id
    : null;

  const requestedStylePreset = raw.stylePreset === null || raw.stylePreset === undefined
    ? null
    : textValue(raw.stylePreset, "", "stylePreset");
  const stylePresetDefinition = presetById(requestedStylePreset);
  if (requestedStylePreset && !stylePresetDefinition) throw new Error("stylePreset has an unsupported value.");
  const stylePreset = stylePresetDefinition
    && styles.length === stylePresetDefinition.pairsWith.length
    && stylePresetDefinition.pairsWith.every((style, index) => styles[index] === style)
    ? stylePresetDefinition.id
    : null;

  return {
    ...defaults,
    target: enumValue(raw.target, TARGETS, defaults.target, "target"),
    project: textValue(raw.project, defaults.project, "project"),
    iconClass: enumValue(raw.iconClass, ICON_CLASSES, defaults.iconClass, "iconClass"),
    purpose: textValue(raw.purpose, defaults.purpose, "purpose"),
    audience: textValue(raw.audience, defaults.audience, "audience"),
    territories: textValue(raw.territories, defaults.territories, "territories"),
    avoid: textValue(raw.avoid, defaults.avoid, "avoid"),
    styles,
    stylePreset,
    axes,
    characterMode: mode,
    characterPreset,
    smallest: enumValue(raw.smallest, SMALLEST_SIZES, defaults.smallest, "smallest"),
    backgrounds: textValue(raw.backgrounds, defaults.backgrounds, "backgrounds"),
    palette: textValue(raw.palette, defaults.palette, "palette"),
    deliveryNotes: textValue(raw.deliveryNotes, defaults.deliveryNotes, "deliveryNotes")
  };
}

const display = (value: string, fallback = "not specified") => value.trim() || fallback;

export function buildPrompt(state: BriefState): string {
  const styles = state.styles.length ? state.styles.join(", ") : "open; choose from the brief";
  const preset = presetById(state.characterPreset);
  const opening = state.target === "claude-code"
    ? "/icon-design:icon-design\nStart at discovery and stop after the discovery handoff."
    : state.target === "any-chatbot"
      ? "Run a staged icon-design process. Start at discovery and stop after the discovery handoff."
      : "Use $icon-design. Start at discovery and stop after the discovery handoff.";
  return [
    opening,
    `Project: ${display(state.project, "unnamed project")} (${state.iconClass}).`,
    `Purpose: ${display(state.purpose)}.`,
    `Audience/context: ${display(state.audience)}.`,
    `Metaphor territories: ${display(state.territories, "derive several useful territories from the purpose")}.`,
    `Style references: ${styles}. Do not imitate an existing mark.`,
    `Character${preset ? ` (${preset.name})` : ""}: ${axisSummary(state.axes)}.`,
    `Color: monochrome currentColor master; color only in derived assets. Palette constraints: ${display(state.palette, "none supplied")}.`,
    `Verification: smallest size ${state.smallest}; backgrounds ${display(state.backgrounds)}.`,
    `Avoid: ${display(state.avoid, "obvious clichés and competitor lookalikes")}.`,
    "Discovery output: 20 genuinely distinct representations arranged as five useful territories with four structurally different constructions each. Use IDs D1-01 through D1-20, one currentColor SVG per direction, a kalebtec.icon-round.v2 concepts.json, and matching numbered PNG and standalone HTML review sheets. Show large, lockup, dark-background, app-tile, and 16/24/32 px views.",
    "After the sheet, summarize the territories briefly and wait for a numbered selection or another discovery instruction.",
    "After final approval, export the complete package: canonical and fixed SVGs, favicon PNG/ICO/SVG, app icon, social avatar, Composer layers, comparison sheets, source, README, license, and reproducible zip.",
    state.deliveryNotes ? `Additional delivery notes: ${state.deliveryNotes}.` : ""
  ].filter(Boolean).join("\n");
}

export function completionCount(state: BriefState): number {
  return [
    state.project,
    state.purpose,
    state.audience,
    state.territories,
    state.styles.length,
    state.characterPreset || state.characterMode === "custom"
  ].filter(Boolean).length;
}

export function slug(value: string): string {
  return value
    .normalize("NFKC")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, "-")
    .replace(/^-|-$/g, "") || "project";
}

export function hasBriefChanges(state: BriefState): boolean {
  return JSON.stringify(state) !== JSON.stringify(createDefaultBrief());
}
