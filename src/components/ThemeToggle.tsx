import type { Theme } from "../lib/theme";

export function ThemeToggle(props: { theme: Theme; onToggle: () => void }) {
  const dark = () => props.theme === "dark";

  return (
    <button
      type="button"
      class="theme-toggle"
      aria-label="Dark theme"
      aria-pressed={dark()}
      title={dark() ? "Switch to light theme" : "Switch to dark theme"}
      onClick={props.onToggle}
    >
      <svg viewBox="0 0 20 20" aria-hidden="true">
        <path d="M15.7 13.2A6.6 6.6 0 0 1 6.8 4.3 6.8 6.8 0 1 0 15.7 13.2Z" fill="currentColor" />
      </svg>
      <span>Dark</span>
    </button>
  );
}
