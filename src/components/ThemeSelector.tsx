import { For } from "solid-js";
import type { ThemePreference } from "../lib/theme";

const THEME_OPTIONS: ThemePreference[] = ["system", "light", "dark"];

export function ThemeSelector(props: {
  preference: ThemePreference;
  onChange: (preference: ThemePreference) => void;
}) {
  return (
    <label class="theme-selector">
      <span class="sr-only">Theme</span>
      <select
        value={props.preference}
        title="Theme preference"
        onChange={(event) => props.onChange(event.currentTarget.value as ThemePreference)}
      >
        <For each={THEME_OPTIONS}>
          {(option) => <option value={option}>{option[0].toUpperCase() + option.slice(1)}</option>}
        </For>
      </select>
    </label>
  );
}
