import { describe, expect, it } from "vitest";
import { buildPrompt, createDefaultBrief, hasBriefChanges, normalizeBrief, slug } from "./brief";

describe("icon brief", () => {
  it("defaults to guided character configuration and complete delivery", () => {
    const brief = createDefaultBrief();
    expect(brief.characterMode).toBe("guided");
    expect(brief.characterPreset).toBeNull();
    expect(brief.stylePreset).toBeNull();
    expect(brief.conceptCount).toBe(20);
    expect(brief.fullPackage).toBe(true);
  });

  it("generates a discovery-only prompt with the final package promised", () => {
    const prompt = buildPrompt({
      ...createDefaultBrief(),
      project: "Relay",
      purpose: "Make handoffs clear"
    });
    expect(prompt).toContain("D1-01 through D1-20");
    expect(prompt).toContain("wait for a numbered selection");
    expect(prompt).toContain("complete package");
  });

  it("imports older v1 briefs without the new character mode fields", () => {
    const original = createDefaultBrief();
    const legacy = { ...original } as Record<string, unknown>;
    delete legacy.characterMode;
    delete legacy.characterPreset;
    delete legacy.stylePreset;
    const imported = normalizeBrief(legacy);
    expect(imported.characterMode).toBe("guided");
    expect(imported.characterPreset).toBeNull();
    expect(imported.stylePreset).toBeNull();
    expect(imported.axes).toEqual(original.axes);
  });

  it("rejects invalid character values", () => {
    const brief = createDefaultBrief();
    expect(() => normalizeBrief({ ...brief, axes: { ...brief.axes, density: 8 } })).toThrow(
      "density must be an integer from 1 to 5"
    );
  });

  it("rejects unsupported imported selections", () => {
    const brief = createDefaultBrief();
    expect(() => normalizeBrief({ ...brief, target: "unknown-chatbot" })).toThrow(
      "target has an unsupported value"
    );
    expect(() => normalizeBrief({ ...brief, smallest: "0 px" })).toThrow(
      "smallest has an unsupported value"
    );
  });

  it("normalizes inconsistent preset metadata without changing the chosen axes or styles", () => {
    const brief = createDefaultBrief();
    const imported = normalizeBrief({
      ...brief,
      characterPreset: "quiet-precision",
      stylePreset: "quiet-precision",
      styles: ["humanist"]
    });
    expect(imported.characterPreset).toBeNull();
    expect(imported.stylePreset).toBeNull();
    expect(imported.axes).toEqual(brief.axes);
    expect(imported.styles).toEqual(["humanist"]);
  });

  it("detects non-content changes before replacing an imported brief", () => {
    expect(hasBriefChanges(createDefaultBrief())).toBe(false);
    expect(hasBriefChanges({ ...createDefaultBrief(), target: "any-chatbot" })).toBe(true);
  });

  it("keeps non-Latin project names usable in filenames", () => {
    expect(slug("アイコン 設計")).toBe("アイコン-設計");
    expect(slug("---")).toBe("project");
  });
});
