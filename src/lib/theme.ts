export type Theme = "light" | "dark";
export type ThemePreference = Theme | "system";

export const THEME_STORAGE_KEY = "kalebtec.icon-brief.theme";

export function normalizeThemePreference(value: unknown): ThemePreference {
  return value === "light" || value === "dark" ? value : "system";
}

export function resolveTheme(preference: unknown, prefersDark: boolean): Theme {
  if (preference === "light" || preference === "dark") return preference;
  return prefersDark ? "dark" : "light";
}

export function themeColor(theme: Theme): string {
  return theme === "dark" ? "#080f11" : "#f1f0e4";
}
