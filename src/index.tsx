import { render } from "solid-js/web";
import App from "./App";
import "./styles.css";

const root = document.getElementById("root");
if (!root) throw new Error("App root not found");

render(() => <App />, root);

declare global {
  interface Window {
    __ICON_BRIEF_BUILDER__?: {
      schema: string;
      version: string;
    };
  }
}

window.__ICON_BRIEF_BUILDER__ = {
  schema: "kalebtec.icon-brief.v1",
  version: "1.5.0"
};
