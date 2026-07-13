import { For, Show, createMemo, createSignal } from "solid-js";
import { CHARACTER_PRESETS, type CharacterPreset } from "../data/presets";
import {
  AXIS_META,
  AXIS_NAMES,
  axesFromBits,
  characterName,
  permutationBits,
  permutationLabel,
  quantizedBits,
  type AxisName,
  type CharacterAxes
} from "../lib/character";
import type { CharacterMode } from "../lib/brief";
import { Glyph } from "./Glyph";

const PERMUTATIONS = Array.from({ length: 64 }, (_, index) => {
  const bits = permutationBits(index);
  return {
    index,
    bits,
    key: bits.join(""),
    axes: axesFromBits(bits),
    label: permutationLabel(bits)
  };
});

interface CharacterConfiguratorProps {
  axes: CharacterAxes;
  mode: CharacterMode;
  presetId: string | null;
  onMode: (mode: CharacterMode) => void;
  onPreset: (preset: CharacterPreset) => void;
  onAxes: (axes: CharacterAxes) => void;
}

export function CharacterConfigurator(props: CharacterConfiguratorProps) {
  const [hoveredMix, setHoveredMix] = createSignal<string | null>(null);
  const selectedKey = createMemo(() => quantizedBits(props.axes).join(""));
  const exactMatrixValue = createMemo(() => AXIS_NAMES.every((name) => props.axes[name] === 2 || props.axes[name] === 4));
  const selectedLabel = createMemo(() => permutationLabel(quantizedBits(props.axes)));

  const setAxis = (name: AxisName, value: number) => {
    props.onAxes({ ...props.axes, [name]: value });
  };

  return (
    <div class="character-configurator">
      <section class="character-overview" aria-label="Current character">
        <div class="current-glyph-frame">
          <Glyph
            axes={props.axes}
            id="character-current"
            class="current-glyph"
            label={`Current character: ${characterName(props.axes)}`}
          />
        </div>
        <div class="character-summary">
          <span class="kicker">Current character</span>
          <h3>{characterName(props.axes)}</h3>
          <p>The same axis values drive this specimen, every preset preview, and each matrix cell.</p>
          <div class="axis-chips" aria-label="Current character values">
            <For each={AXIS_NAMES}>
              {(name) => <span>{AXIS_META[name].label} {props.axes[name]}</span>}
            </For>
          </div>
        </div>
      </section>

      <div class="mode-switch" role="group" aria-label="Character configuration mode">
        <button
          type="button"
          classList={{ active: props.mode === "guided" }}
          aria-pressed={props.mode === "guided"}
          onClick={() => props.onMode("guided")}
        >
          <strong>Guided</strong><span>Start from a useful character preset</span>
        </button>
        <button
          type="button"
          classList={{ active: props.mode === "custom" }}
          aria-pressed={props.mode === "custom"}
          onClick={() => props.onMode("custom")}
        >
          <strong>Custom</strong><span>Tune six axes and inspect all 64 mixes</span>
        </button>
      </div>

      <Show when={props.mode === "guided"}>
        <section class="preset-section">
          <div class="section-heading">
            <div><span class="kicker">Choose one</span><h3>Ready-made character directions</h3></div>
            <p>Presets set the six axes. Tagged styles follow while you compare presets; reference choices you made yourself stay untouched.</p>
          </div>
          <div class="preset-grid">
            <For each={CHARACTER_PRESETS}>
              {(preset) => (
                <button
                  type="button"
                  class="preset-card"
                  classList={{ selected: props.presetId === preset.id }}
                  aria-pressed={props.presetId === preset.id}
                  onClick={() => props.onPreset(preset)}
                >
                  <span class="preset-preview"><Glyph axes={preset.axes} id={`preset-${preset.id}`} /></span>
                  <span class="preset-copy">
                    <strong>{preset.name}</strong>
                    <small>{preset.note}</small>
                    <span class="preset-tags">
                      <For each={preset.pairsWith}>{(style) => <span>{style}</span>}</For>
                    </span>
                  </span>
                </button>
              )}
            </For>
          </div>
          <button type="button" class="text-button" onClick={() => props.onMode("custom")}>Fine-tune this character →</button>
        </section>
      </Show>

      <Show when={props.mode === "custom"}>
        <section class="custom-section">
          <div class="section-heading">
            <div><span class="kicker">Fine-tune</span><h3>Six independent character axes</h3></div>
            <p>The large specimen uses the full 1–5 values. Matrix landmarks use 2 and 4 so choosing one always reproduces its preview exactly.</p>
          </div>
          <div class="axes">
            <For each={AXIS_NAMES}>
              {(name) => (
                <div class="axis-control">
                  <div class="axis-label">
                    <label for={`axis-${name}`}>{AXIS_META[name].label}</label>
                    <output for={`axis-${name}`}>{props.axes[name]} · {AXIS_META[name].words[props.axes[name] - 1]}</output>
                  </div>
                  <input
                    id={`axis-${name}`}
                    name={name}
                    type="range"
                    min="1"
                    max="5"
                    value={props.axes[name]}
                    aria-valuetext={AXIS_META[name].words[props.axes[name] - 1]}
                    onInput={(event) => setAxis(name, Number(event.currentTarget.value))}
                  />
                  <div class="axis-ends"><span>{AXIS_META[name].low}</span><span>{AXIS_META[name].high}</span></div>
                </div>
              )}
            </For>
          </div>

          <div class="matrix-section">
            <div class="matrix-heading">
              <div><span class="kicker">Reference map</span><h3>64 lower/higher landmarks</h3></div>
              <p>Rows combine complexity, geometry, and energy. Columns combine playfulness, density, and novelty.</p>
            </div>
            <div class="matrix-scroll">
              <div class="character-matrix" role="radiogroup" aria-label="Character permutation landmarks" aria-describedby="matrix-status">
                <For each={PERMUTATIONS}>
                  {(permutation) => (
                    <label
                      class="matrix-cell"
                      classList={{ nearest: !exactMatrixValue() && selectedKey() === permutation.key }}
                      onMouseEnter={() => setHoveredMix(permutation.label)}
                      onMouseLeave={() => setHoveredMix(null)}
                    >
                      <input
                        type="radio"
                        name="character-permutation"
                        value={permutation.key}
                        checked={exactMatrixValue() && selectedKey() === permutation.key}
                        tabIndex={selectedKey() === permutation.key ? 0 : -1}
                        aria-label={`Apply ${permutation.label}`}
                        onFocus={() => setHoveredMix(permutation.label)}
                        onBlur={() => setHoveredMix(null)}
                        onChange={() => props.onAxes({ ...permutation.axes })}
                      />
                      <Glyph axes={permutation.axes} id={`matrix-${permutation.index}`} />
                    </label>
                  )}
                </For>
              </div>
            </div>
            <p id="matrix-status" class="matrix-status">
              <Show when={hoveredMix()} fallback={exactMatrixValue() ? `Selected landmark: ${selectedLabel()}.` : `Nearest landmark: ${selectedLabel()}. Your exact slider values remain in the large specimen.`}>
                {(label) => `Preview: ${label()}.`}
              </Show>
            </p>
          </div>
        </section>
      </Show>
    </div>
  );
}
