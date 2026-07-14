// @vitest-environment jsdom

import axe from "axe-core";
import { render } from "solid-js/web";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

let dispose: (() => void) | undefined;
let setSystemPreference: (dark: boolean) => void;

function buttonNamed(label: string): HTMLButtonElement {
  const button = [...document.querySelectorAll<HTMLButtonElement>("button")]
    .find((candidate) => candidate.textContent?.includes(label));
  if (!button) throw new Error(`Missing button: ${label}`);
  return button;
}

async function expectNoViolations() {
  await Promise.resolve();
  const results = await axe.run(document, {
    rules: {
      "color-contrast": { enabled: false }
    }
  });
  expect(results.violations, results.violations.map((violation) => `${violation.id}: ${violation.help}`).join("\n")).toEqual([]);
}

beforeEach(() => {
  document.documentElement.lang = "en";
  document.documentElement.removeAttribute("data-theme");
  document.body.innerHTML = '<div id="root"></div>';
  localStorage.clear();
  const listeners = new Set<(event: MediaQueryListEvent) => void>();
  setSystemPreference = (dark) => listeners.forEach((listener) => listener({ matches: dark } as MediaQueryListEvent));
  vi.stubGlobal("matchMedia", vi.fn().mockReturnValue({
    matches: false,
    media: "(prefers-color-scheme: dark)",
    addEventListener: (_type: string, listener: (event: MediaQueryListEvent) => void) => listeners.add(listener),
    removeEventListener: (_type: string, listener: (event: MediaQueryListEvent) => void) => listeners.delete(listener)
  }));
  dispose = render(() => <App />, document.getElementById("root")!);
});

afterEach(() => {
  dispose?.();
  dispose = undefined;
  vi.unstubAllGlobals();
  document.body.innerHTML = "";
});

describe("rendered accessibility", () => {
  it("has no automated violations on the purpose step", async () => {
    await expectNoViolations();
  });

  it("has no automated violations on reference and character controls", async () => {
    const project = document.querySelector<HTMLInputElement>('input[placeholder="Northstar"]')!;
    project.value = "Accessibility review";
    project.dispatchEvent(new InputEvent("input", { bubbles: true }));
    const purpose = document.querySelector<HTMLTextAreaElement>("textarea[required]")!;
    purpose.value = "Create an accessible icon brief";
    purpose.dispatchEvent(new InputEvent("input", { bubbles: true }));

    buttonNamed("Choose references").click();
    await expectNoViolations();

    buttonNamed("Set character").click();
    await expectNoViolations();

    buttonNamed("Custom").click();
    await expectNoViolations();

    document.querySelector<HTMLDetailsElement>(".delivery-options summary")!.click();
    await expectNoViolations();
  });

  it("has no automated violations in the help dialog", async () => {
    buttonNamed("How it works").click();
    expect(document.querySelector("dialog")?.hasAttribute("open")).toBe(true);
    await expectNoViolations();
  });

  it("exposes and persists the theme control state", () => {
    const toggle = document.querySelector<HTMLButtonElement>(".theme-toggle")!;
    expect(toggle.getAttribute("aria-pressed")).toBe("false");
    toggle.click();
    expect(document.documentElement.dataset.theme).toBe("dark");
    expect(toggle.getAttribute("aria-pressed")).toBe("true");
    expect(localStorage.getItem("kalebtec.icon-brief.theme")).toBe("dark");
  });

  it("follows system changes until a theme is chosen", () => {
    const toggle = document.querySelector<HTMLButtonElement>(".theme-toggle")!;
    setSystemPreference(true);
    expect(document.documentElement.dataset.theme).toBe("dark");
    expect(localStorage.getItem("kalebtec.icon-brief.theme")).toBeNull();

    toggle.click();
    expect(document.documentElement.dataset.theme).toBe("light");
    setSystemPreference(true);
    expect(document.documentElement.dataset.theme).toBe("light");
  });
});
