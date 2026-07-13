import { Show } from "solid-js";
import { glyphGeometry, type CharacterAxes } from "../lib/character";

interface GlyphProps {
  axes: CharacterAxes;
  id: string;
  class?: string;
  label?: string;
}

export function Glyph(props: GlyphProps) {
  const geometry = () => glyphGeometry(props.axes);
  const maskId = () => `character-glyph-mask-${props.id.replace(/[^a-zA-Z0-9_-]/g, "-")}`;

  return (
    <svg
      viewBox="0 0 64 64"
      class={props.class}
      role={props.label ? "img" : undefined}
      aria-label={props.label}
      aria-hidden={props.label ? undefined : "true"}
    >
      <Show when={props.label} keyed>
        {(label) => <title>{label}</title>}
      </Show>
      <defs>
        <mask id={maskId()} maskUnits="userSpaceOnUse" x="0" y="0" width="64" height="64">
          <rect width="64" height="64" fill="white" />
          <circle
            cx={geometry().notch.x}
            cy={geometry().notch.y}
            r={geometry().notch.radius}
            fill="black"
            opacity={geometry().notch.opacity}
          />
          <circle
            cx={geometry().detailOne.x}
            cy={geometry().detailOne.y}
            r={geometry().detailOne.radius}
            fill="black"
            opacity={geometry().detailOne.opacity}
          />
          <rect
            x={geometry().detailTwo.x}
            y={geometry().detailTwo.y}
            width={geometry().detailTwo.width}
            height={geometry().detailTwo.height}
            rx={geometry().detailTwo.radius}
            fill="black"
            opacity={geometry().detailTwo.opacity}
          />
        </mask>
      </defs>
      <g
        transform={`rotate(${geometry().rotation} 32 32)`}
        fill="currentColor"
        mask={`url(#${maskId()})`}
      >
        <rect
          x={geometry().left.x}
          y={geometry().left.y}
          width={geometry().left.width}
          height={geometry().left.height}
          rx={geometry().cornerRadius}
        />
        <rect
          x={geometry().right.x}
          y={geometry().right.y}
          width={geometry().right.width}
          height={geometry().right.height}
          rx={geometry().cornerRadius}
          transform={`rotate(${geometry().right.rotation} ${geometry().right.centerX} ${geometry().right.centerY})`}
        />
        <rect
          x={geometry().bridge.x}
          y={geometry().bridge.y}
          width={geometry().bridge.width}
          height={geometry().bridge.height}
          rx={geometry().bridge.radius}
        />
      </g>
    </svg>
  );
}
