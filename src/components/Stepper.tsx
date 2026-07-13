import { For } from "solid-js";

const STEPS = [
  { label: "Purpose", hint: "Set the job" },
  { label: "References", hint: "Choose a language" },
  { label: "Character", hint: "Set the feel" }
] as const;

export function Stepper(props: { current: number; onSelect: (step: number) => void }) {
  return (
    <nav class="stepper" aria-label="Brief builder progress">
      <div class="stepper-heading">
        <span>Build your brief</span>
        <span>Step {props.current + 1} of {STEPS.length}</span>
      </div>
      <progress value={props.current + 1} max={STEPS.length} aria-label={`Step ${props.current + 1} of ${STEPS.length}`} />
      <ol>
        <For each={STEPS}>
          {(step, index) => (
            <li classList={{ complete: index() < props.current }}>
              <button
                type="button"
                classList={{ current: index() === props.current }}
                aria-current={index() === props.current ? "step" : undefined}
                onClick={() => props.onSelect(index())}
              >
                <span class="step-number">{index() + 1}</span>
                <span class="step-copy"><strong>{step.label}</strong><small>{step.hint}</small></span>
              </button>
            </li>
          )}
        </For>
      </ol>
    </nav>
  );
}
