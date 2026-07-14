export function HowItWorks(props: { setDialog: (element: HTMLDialogElement) => void }) {
  return (
    <dialog ref={props.setDialog} class="how-dialog" aria-labelledby="how-title" aria-describedby="how-description">
      <form method="dialog">
        <div class="dialog-head">
          <div><span class="kicker">After this brief</span><h2 id="how-title">Three deliberate stages.</h2></div>
          <button type="submit" class="icon-button" aria-label="Close how it works">×</button>
        </div>
        <ol class="how-list">
          <li><span>01</span><div><strong>Discover</strong><p>Explore five territories and 20 genuinely different ideas on matching PNG and HTML review sheets.</p></div></li>
          <li><span>02</span><div><strong>Refine</strong><p>Choose one or a shortlist. Parents stay visible while focused variants are compared by number.</p></div></li>
          <li><span>03</span><div><strong>Finish</strong><p>Approve a direction and export the complete SVG, favicon, app-icon, source, and zip package.</p></div></li>
        </ol>
        <p id="how-description" class="dialog-note">The generated prompt requests discovery only, so the process pauses for your choice instead of guessing a final answer.</p>
        <button type="submit" class="button primary">Got it</button>
      </form>
    </dialog>
  );
}
