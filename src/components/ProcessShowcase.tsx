import { For } from "solid-js";
import { KalebtecMark } from "./KalebtecMark";

const discoveryCells = Array.from({ length: 20 }, (_, index) => index);
const refinementCells = Array.from({ length: 8 }, (_, index) => index);

export function ProcessShowcase() {
  return (
    <section class="process-showcase" aria-labelledby="process-title">
      <div class="process-heading">
        <div>
          <span class="kicker">One process, two review formats</span>
          <h2 id="process-title">A clear record at every decision.</h2>
        </div>
        <p>
          Each working round produces a fixed PNG for sharing and a standalone
          HTML page for selecting IDs and copying the next request.
        </p>
      </div>

      <div class="process-grid">
        <article class="process-card">
          <div class="process-card-topline"><span>01 / Discovery</span><span>D1</span></div>
          <div class="sheet-mini discovery-mini" aria-hidden="true">
            <div class="sheet-mini-head"><i /><i /></div>
            <div class="sheet-mini-grid">
              <For each={discoveryCells}>{(cell) => <i data-territory={Math.floor(cell / 4)} />}</For>
            </div>
          </div>
          <h3>Five territories, twenty ideas</h3>
          <p>Four structurally different constructions per territory, numbered and shown in consistent contexts.</p>
          <span class="format-tag">PNG + interactive HTML</span>
        </article>

        <article class="process-card">
          <div class="process-card-topline"><span>02 / Refinement</span><span>R1</span></div>
          <div class="sheet-mini refinement-mini" aria-hidden="true">
            <div class="control-mini"><i /><span /><span /></div>
            <div class="sheet-mini-grid refinement-cells">
              <For each={refinementCells}>{(_, index) => <i class={index() === 3 ? "selected" : ""} />}</For>
            </div>
          </div>
          <h3>The parent stays in the room</h3>
          <p>Controls and benchmarks remain visible, so a new variant has to earn the decision—and the parent can still win.</p>
          <span class="format-tag">Lineage + ordered selection</span>
        </article>

        <article class="process-card final-process-card">
          <div class="process-card-topline"><span>03 / Final</span><span>Kalebtec</span></div>
          <div class="final-mark-stage">
            <KalebtecMark class="final-mark" />
            <div class="native-mark-row" aria-hidden="true">
              <KalebtecMark /><KalebtecMark /><KalebtecMark />
            </div>
          </div>
          <h3>Kalebtec logo</h3>
          <p>Two senior partners stay distinct, then meet at one engineering junction. The chosen parent survived refinement intact.</p>
          <span class="format-tag">Complete production package</span>
        </article>
      </div>
    </section>
  );
}
