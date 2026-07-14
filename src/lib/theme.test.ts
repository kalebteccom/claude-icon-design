import { describe, expect, it } from "vitest";
import { oppositeTheme, resolveTheme, themeColor } from "./theme";

describe("site theme", () => {
  it("keeps an explicit saved theme", () => {
    expect(resolveTheme("light", true)).toBe("light");
    expect(resolveTheme("dark", false)).toBe("dark");
  });

  it("falls back to the system preference", () => {
    expect(resolveTheme(null, true)).toBe("dark");
    expect(resolveTheme("unexpected", false)).toBe("light");
  });

  it("switches between the two supported themes", () => {
    expect(oppositeTheme("light")).toBe("dark");
    expect(oppositeTheme("dark")).toBe("light");
  });

  it("uses the page colors for browser chrome", () => {
    expect(themeColor("light")).toBe("#f1f0e4");
    expect(themeColor("dark")).toBe("#080f11");
  });
});
