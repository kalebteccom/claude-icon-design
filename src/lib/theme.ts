export type Theme = "light" | "dark";

export const THEME_STORAGE_KEY = "kalebtec.icon-brief.theme";

export function resolveTheme(value: unknown, prefersDark: boolean): Theme {
  if (value === "light" || value === "dark") return value;
  return prefersDark ? "dark" : "light";
}

export function oppositeTheme(theme: Theme): Theme {
  return theme === "dark" ? "light" : "dark";
}

export function themeColor(theme: Theme): string {
  return theme === "dark" ? "#080f11" : "#f1f0e4";
}
