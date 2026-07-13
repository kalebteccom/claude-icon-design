import { Match, Switch } from "solid-js";

export const STYLE_OPTIONS = [
  { id: "geometric", name: "Geometric", note: "Primitives, ratios, crisp structure" },
  { id: "monoline", name: "Monoline", note: "One weight, open motion, light touch" },
  { id: "solid glyph", name: "Solid glyph", note: "Bold silhouette, compact at small sizes" },
  { id: "negative space", name: "Negative space", note: "A second idea cut from one mass" },
  { id: "modular", name: "Modular", note: "Repeated units and systematic assembly" },
  { id: "organic", name: "Organic", note: "Living curves and uneven balance" },
  { id: "technical", name: "Technical", note: "Measured joints and engineered detail" },
  { id: "humanist", name: "Humanist", note: "Warm rhythm and hand-aware proportions" },
  { id: "pixel informed", name: "Pixel-informed", note: "Stepped form made for tiny rendering" },
  { id: "emblem", name: "Emblem", note: "Contained, ownable, badge-like presence" },
  { id: "monogram", name: "Monogram", note: "Letter structure without typesetting" },
  { id: "dimensional", name: "Dimensional", note: "Depth in derived tiles, flat vector master" }
] as const;

export type StyleId = (typeof STYLE_OPTIONS)[number]["id"];

export function StyleSpecimen(props: { style: StyleId; label?: string }) {
  return (
    <svg viewBox="0 0 64 64" role={props.label ? "img" : undefined} aria-label={props.label} aria-hidden={props.label ? undefined : "true"}>
      <Switch>
        <Match when={props.style === "geometric"}>
          <path d="M12 44 32 10l20 34-20 10Z" fill="none" stroke="currentColor" stroke-width="5" stroke-linejoin="round" />
          <circle cx="32" cy="36" r="7" fill="currentColor" />
        </Match>
        <Match when={props.style === "monoline"}>
          <path d="M14 44c0-17 10-28 20-28 9 0 16 7 16 16 0 10-8 17-18 17H19" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" />
        </Match>
        <Match when={props.style === "solid glyph"}>
          <path d="M12 18c0-4 3-7 7-7h16c10 0 17 7 17 17 0 12-10 23-28 27V43H19c-4 0-7-3-7-7Z" fill="currentColor" />
        </Match>
        <Match when={props.style === "negative space"}>
          <path d="M8 32 31 9l25 23-25 23Zm19-8v16l12-8Z" fill="currentColor" fill-rule="evenodd" />
        </Match>
        <Match when={props.style === "modular"}>
          <rect x="9" y="9" width="20" height="20" rx="4" fill="currentColor" />
          <rect x="35" y="9" width="20" height="20" rx="10" fill="currentColor" />
          <rect x="9" y="35" width="20" height="20" rx="10" fill="currentColor" />
          <path d="M35 35h20v20H35z" fill="currentColor" />
        </Match>
        <Match when={props.style === "organic"}>
          <path d="M12 38C7 23 20 9 35 12c15 3 21 21 12 33-8 11-29 11-35-7Z" fill="currentColor" />
          <path d="M22 35c7-1 11-6 15-14" fill="none" stroke="var(--specimen-cutout)" stroke-width="4" stroke-linecap="round" />
        </Match>
        <Match when={props.style === "technical"}>
          <path d="M10 20h13V10h18v10h13v24H41v10H23V44H10Z" fill="none" stroke="currentColor" stroke-width="4" />
          <path d="M23 32h18M32 23v18" stroke="currentColor" stroke-width="3" />
        </Match>
        <Match when={props.style === "humanist"}>
          <path d="M12 47c6-2 8-8 8-15V14h9v18c0 7 4 11 9 11s9-4 9-11V14h9v18c0 14-8 23-20 23-6 0-11-2-15-6-2 3-5 5-9 6Z" fill="currentColor" />
        </Match>
        <Match when={props.style === "pixel informed"}>
          <path d="M10 10h18v9h9v9h17v26H28v-9h-9v-9h-9Z" fill="currentColor" />
        </Match>
        <Match when={props.style === "emblem"}>
          <path d="M32 7 53 19v25L32 57 11 44V19Z" fill="none" stroke="currentColor" stroke-width="4" />
          <path d="m22 39 10-20 10 20-10-5Z" fill="currentColor" />
        </Match>
        <Match when={props.style === "monogram"}>
          <path d="M12 51V13l20 25 20-25v38" fill="none" stroke="currentColor" stroke-width="7" stroke-linejoin="round" />
        </Match>
        <Match when={props.style === "dimensional"}>
          <path d="m32 7 23 13-23 13L9 20Z" fill="currentColor" />
          <path d="m9 26 23 13 23-13v12L32 51 9 38Z" fill="currentColor" opacity=".58" />
        </Match>
      </Switch>
    </svg>
  );
}
