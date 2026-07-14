import { For, createEffect, createMemo, createSignal, onMount } from "solid-js";
import { CharacterConfigurator } from "./components/CharacterConfigurator";
import { Glyph } from "./components/Glyph";
import { HowItWorks } from "./components/HowItWorks";
import { KalebtecMark } from "./components/KalebtecMark";
import { ProcessShowcase } from "./components/ProcessShowcase";
import { STYLE_OPTIONS, StyleSpecimen, type StyleId } from "./components/StyleSpecimen";
import { Stepper } from "./components/Stepper";
import type { CharacterPreset } from "./data/presets";
import {
  ICON_CLASSES,
  LEGACY_STORAGE_KEY,
  SMALLEST_SIZES,
  STORAGE_KEY,
  TARGETS,
  buildPrompt,
  completionCount,
  createDefaultBrief,
  hasBriefChanges,
  normalizeBrief,
  slug,
  type BriefState,
  type CharacterMode,
  type IconClass,
  type SmallestSize,
  type Target
} from "./lib/brief";
import { characterName, type CharacterAxes } from "./lib/character";

const TARGET_LABELS: Record<Target, string> = {
  codex: "Codex",
  "claude-code": "Claude Code",
  "any-chatbot": "Another chatbot"
};

function App() {
  const [state, setState] = createSignal<BriefState>(createDefaultBrief());
  const [activeStep, setActiveStep] = createSignal(0);
  const [toast, setToast] = createSignal("");
  const [ready, setReady] = createSignal(false);
  const prompt = createMemo(() => buildPrompt(state()));
  const completed = createMemo(() => completionCount(state()));
  let toastTimer: number | undefined;
  let promptOutput: HTMLTextAreaElement | undefined;
  let projectInput: HTMLInputElement | undefined;
  let purposeInput: HTMLTextAreaElement | undefined;
  let importInput: HTMLInputElement | undefined;
  let howDialog: HTMLDialogElement | undefined;

  const notify = (message: string) => {
    window.clearTimeout(toastTimer);
    setToast(message);
    toastTimer = window.setTimeout(() => setToast(""), 3000);
  };

  const patchState = (patch: Partial<BriefState>) => {
    setState((current) => ({ ...current, ...patch }));
  };

  onMount(() => {
    for (const key of [STORAGE_KEY, LEGACY_STORAGE_KEY]) {
      try {
        const saved = localStorage.getItem(key);
        if (!saved) continue;
        setState(normalizeBrief(JSON.parse(saved)));
        break;
      } catch {
        try {
          localStorage.removeItem(key);
        } catch {
          // The builder still works without persistent browser storage.
        }
      }
    }
    setReady(true);
  });

  createEffect(() => {
    const current = state();
    if (!ready()) return;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(current));
    } catch {
      // Export remains available when browser storage is disabled.
    }
  });

  const showStep = (step: number) => {
    const nextStep = Math.max(0, Math.min(2, step));
    setActiveStep(nextStep);
    window.setTimeout(() => {
      document.querySelector<HTMLElement>(`[data-step-panel="${nextStep}"] h2`)?.focus();
    });
  };

  const validatePurpose = () => {
    if (!state().project.trim()) {
      showStep(0);
      window.setTimeout(() => projectInput?.focus());
      projectInput?.reportValidity();
      notify("Add a project name before exporting.");
      return false;
    }
    if (!state().purpose.trim()) {
      showStep(0);
      window.setTimeout(() => purposeInput?.focus());
      purposeInput?.reportValidity();
      notify("Describe what the icon should communicate.");
      return false;
    }
    return true;
  };

  const nextStep = () => {
    if (activeStep() === 0 && !validatePurpose()) return;
    showStep(activeStep() + 1);
  };

  const selectStep = (step: number) => {
    if (step > 0 && !validatePurpose()) return;
    showStep(step);
  };

  const toggleStyle = (style: StyleId, input: HTMLInputElement) => {
    const checked = input.checked;
    if (checked && !state().styles.includes(style) && state().styles.length >= 3) {
      input.checked = false;
      notify("Choose up to three style references.");
      return;
    }
    const styles = checked
      ? [...state().styles, style]
      : state().styles.filter((candidate) => candidate !== style);
    patchState({ styles, stylePreset: null });
  };

  const choosePreset = (preset: CharacterPreset) => {
    const current = state();
    const referencesFollowPreset = current.styles.length === 0 || current.stylePreset !== null;
    patchState({
      axes: { ...preset.axes },
      characterMode: "guided",
      characterPreset: preset.id,
      styles: referencesFollowPreset ? [...preset.pairsWith] : current.styles,
      stylePreset: referencesFollowPreset ? preset.id : null
    });
  };

  const setCharacterMode = (mode: CharacterMode) => patchState({
    characterMode: mode,
    characterPreset: mode === "custom" ? null : state().characterPreset
  });
  const setAxes = (axes: CharacterAxes) => patchState({ axes, characterMode: "custom", characterPreset: null });

  const copyPrompt = async () => {
    if (!validatePurpose()) return;
    let copied = false;
    try {
      await navigator.clipboard.writeText(prompt());
      copied = true;
    } catch {
      promptOutput?.focus();
      promptOutput?.select();
      copied = document.execCommand("copy");
      window.getSelection()?.removeAllRanges();
    }
    notify(copied ? "Discovery prompt copied." : "Copy failed. Select the prompt and copy it manually.");
  };

  const download = (filename: string, content: string, type: string) => {
    const url = URL.createObjectURL(new Blob([content], { type }));
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  const saveText = () => {
    if (!validatePurpose()) return;
    download(`${slug(state().project)}-icon-brief.txt`, `${prompt()}\n`, "text/plain;charset=utf-8");
    notify("Text brief saved.");
  };

  const saveJson = () => {
    if (!validatePurpose()) return;
    download(`${slug(state().project)}-icon-brief.json`, `${JSON.stringify(state(), null, 2)}\n`, "application/json");
    notify("JSON brief saved.");
  };

  const importJson = async (file: File | undefined) => {
    if (!file) return;
    try {
      const imported = normalizeBrief(JSON.parse(await file.text()));
      if (hasBriefChanges(state()) && !window.confirm("Replace your current brief with the imported one?")) {
        notify("Import canceled.");
        return;
      }
      setState(imported);
      showStep(0);
      notify("Brief imported.");
    } catch (error) {
      notify(error instanceof Error ? error.message : "Could not import this brief.");
    } finally {
      if (importInput) importInput.value = "";
    }
  };

  const reset = () => {
    if (!window.confirm("Reset every brief choice?")) return;
    setState(createDefaultBrief());
    showStep(0);
    notify("Brief reset.");
  };

  const openHow = () => {
    if (typeof howDialog?.showModal === "function") howDialog.showModal();
    else howDialog?.setAttribute("open", "");
  };

  return (
    <div class="app-shell">
      <header class="site-header">
        <a class="brand" href="https://kalebtec.com" aria-label="Kalebtec home">
          <span class="brand-mark" aria-hidden="true"><KalebtecMark /></span><span>Kalebtec</span>
        </a>
        <nav class="header-actions" aria-label="Page links">
          <a href="https://github.com/kalebteccom/claude-icon-design">GitHub</a>
          <button type="button" class="button subtle" onClick={openHow}>How it works</button>
        </nav>
      </header>

      <main>
        <section class="hero">
          <p class="eyebrow">Icon brief builder</p>
          <h1>Make the brief as intentional as the icon.</h1>
          <p>Choose what the mark should communicate, find a visual language, and export a compact prompt for a 20-direction discovery round.</p>
          <div class="hero-notes" aria-label="Builder properties"><span>No account</span><span>No upload</span><span>Works with any chatbot</span></div>
        </section>

        <div class="workspace">
          <form class="builder-panel" onSubmit={(event) => event.preventDefault()}>
            <Stepper current={activeStep()} onSelect={selectStep} />

            <section data-step-panel="0" class="step-panel" hidden={activeStep() !== 0}>
              <div class="panel-heading">
                <span class="kicker">Purpose</span>
                <h2 tabIndex="-1">What should the icon communicate?</h2>
                <p>Start with the job and audience. Meaning gives the discovery round somewhere useful to go.</p>
              </div>
              <div class="field-grid">
                <label class="field"><span>Project or product</span><input ref={projectInput} type="text" required placeholder="Northstar" value={state().project} onInput={(event) => patchState({ project: event.currentTarget.value })} /></label>
                <label class="field"><span>Icon class</span><select value={state().iconClass} onChange={(event) => patchState({ iconClass: event.currentTarget.value as IconClass })}><For each={ICON_CLASSES}>{(value) => <option value={value}>{value}</option>}</For></select></label>
                <label class="field full"><span>Purpose <small>What does it represent or help someone do?</small></span><textarea ref={purposeInput} required placeholder="A privacy-first analytics product that turns noisy activity into a clear direction." value={state().purpose} onInput={(event) => patchState({ purpose: event.currentTarget.value })} /></label>
                <label class="field full"><span>Audience and setting</span><input type="text" placeholder="Independent product teams; shown beside technical tools" value={state().audience} onInput={(event) => patchState({ audience: event.currentTarget.value })} /></label>
                <label class="field full"><span>Promising metaphors or ideas <small>Comma-separated; uncertainty is fine.</small></span><input type="text" placeholder="signal, path, focus, protected window" value={state().territories} onInput={(event) => patchState({ territories: event.currentTarget.value })} /></label>
                <label class="field full"><span>Avoid</span><input type="text" placeholder="generic shield, eye symbol, lightning bolt, competitor lookalikes" value={state().avoid} onInput={(event) => patchState({ avoid: event.currentTarget.value })} /></label>
              </div>
              <div class="step-actions"><button type="button" class="text-button" onClick={reset}>Reset brief</button><button type="button" class="button primary" onClick={nextStep}>Choose references</button></div>
            </section>

            <section data-step-panel="1" class="step-panel" hidden={activeStep() !== 1}>
              <div class="panel-heading">
                <span class="kicker">References</span>
                <h2 tabIndex="-1">Choose up to three visual languages.</h2>
                <p>These are original reference shapes, not logos to copy. Skip this step if you want discovery to stay open.</p>
              </div>
              <fieldset>
                <legend class="sr-only">Style reference sheet</legend>
                <div class="style-grid">
                  <For each={STYLE_OPTIONS}>
                    {(style) => (
                      <label class="style-card">
                        <input
                          type="checkbox"
                          value={style.id}
                          checked={state().styles.includes(style.id)}
                          onChange={(event) => toggleStyle(style.id, event.currentTarget)}
                        />
                        <span class="style-check" aria-hidden="true">✓</span>
                        <StyleSpecimen style={style.id} />
                        <span><strong>{style.name}</strong><small>{style.note}</small></span>
                      </label>
                    )}
                  </For>
                </div>
                <p class="selection-count">{state().styles.length}/3 selected</p>
              </fieldset>
              <div class="step-actions"><button type="button" class="button" onClick={() => showStep(0)}>Back</button><button type="button" class="button primary" onClick={nextStep}>Set character</button></div>
            </section>

            <section data-step-panel="2" class="step-panel" hidden={activeStep() !== 2}>
              <div class="panel-heading">
                <span class="kicker">Character</span>
                <h2 tabIndex="-1">Choose the feel before the form.</h2>
                <p>Use a guided preset for a fast, coherent direction or switch to custom controls when the differences matter.</p>
              </div>
              <CharacterConfigurator
                axes={state().axes}
                mode={state().characterMode}
                presetId={state().characterPreset}
                onMode={setCharacterMode}
                onPreset={choosePreset}
                onAxes={setAxes}
              />

              <details class="delivery-options">
                <summary>Customize delivery</summary>
                <p>The complete SVG, favicon, app-icon, avatar, comparison-sheet, source, and zip package is always included.</p>
                <div class="field-grid">
                  <label class="field"><span>Smallest required size</span><select value={state().smallest} onChange={(event) => patchState({ smallest: event.currentTarget.value as SmallestSize })}><For each={SMALLEST_SIZES}>{(value) => <option value={value}>{value}</option>}</For></select></label>
                  <label class="field"><span>Backgrounds</span><input type="text" value={state().backgrounds} onInput={(event) => patchState({ backgrounds: event.currentTarget.value })} /></label>
                  <label class="field full"><span>Existing palette or constraints</span><input type="text" placeholder="Ink #171815, paper #FBFAF7, accent #C54D34" value={state().palette} onInput={(event) => patchState({ palette: event.currentTarget.value })} /></label>
                  <label class="field full"><span>Additional delivery notes</span><textarea placeholder="Any extra platform, licensing, or handoff constraint." value={state().deliveryNotes} onInput={(event) => patchState({ deliveryNotes: event.currentTarget.value })} /></label>
                </div>
              </details>
              <div class="step-actions"><button type="button" class="button" onClick={() => showStep(1)}>Back</button><button type="button" class="button primary" onClick={copyPrompt}>Copy discovery prompt</button></div>
            </section>
          </form>

          <aside class="output-panel" aria-labelledby="output-title">
            <div class="output-topline"><span>Live brief</span><span>{completed()}/6 signals set</span></div>
            <div class="mini-character">
              <span><Glyph axes={state().axes} id="sidebar-current" /></span>
              <div><small>Character</small><strong>{characterName(state().axes)}</strong></div>
            </div>
            <h2 id="output-title">Discovery prompt</h2>
            <label class="field compact"><span>Paste into</span><select value={state().target} onChange={(event) => patchState({ target: event.currentTarget.value as Target })}><For each={TARGETS}>{(target) => <option value={target}>{TARGET_LABELS[target]}</option>}</For></select></label>
            <p class="target-note">Codex and Claude Code targets expect the <a href="https://github.com/kalebteccom/claude-icon-design#install-in-codex">Icon Design plugin</a>. “Another chatbot” creates a standalone prompt.</p>
            <textarea ref={promptOutput} class="prompt-output" readOnly spellcheck={false} aria-label="Generated discovery prompt" value={prompt()} />
            <div class="export-actions">
              <button type="button" class="button primary" onClick={copyPrompt}>Copy prompt</button>
              <button type="button" class="button" onClick={saveText}>Save text</button>
              <button type="button" class="button" onClick={saveJson}>Save JSON</button>
              <button type="button" class="button" onClick={() => importInput?.click()}>Import</button>
              <input ref={importInput} type="file" accept="application/json,.json" hidden onChange={(event) => importJson(event.currentTarget.files?.[0])} />
            </div>
            <p class="output-note">Requests discovery only, then pauses for a numbered choice before refinement.</p>
            <p class="toast" role="status" aria-live="polite">{toast()}</p>
          </aside>
        </div>
        <ProcessShowcase />
      </main>

      <footer>
        <div class="footer-meta">
          <span class="footer-brand"><KalebtecMark /> Kalebtec Icon Brief</span>
          <span>Local-first · open source · your brief stays in this browser · <a href="/llms.txt">Agent guide</a></span>
          <span>Kalebtec name, logo, and mark © 2026 Kalebtec. All rights reserved.</span>
        </div>
        <span class="footer-credit">Made with love <span class="footer-heart" aria-hidden="true">♥</span> by <a href="https://kalebtec.com">Kalebtec</a></span>
      </footer>
      <HowItWorks setDialog={(element) => { howDialog = element; }} />
    </div>
  );
}

export default App;
