/** Pure-JavaScript DOM harness. No browser, layout, socket or model is started. */
import { parseHTML } from "linkedom";
import { readFile } from "node:fs/promises";
import { createWorkbench } from "../../web/app.js";
const html = await readFile(
  new URL("../../web/index.html", import.meta.url),
  "utf8",
);
export const datasets = Object.fromEntries(
  await Promise.all(
    ["insurance", "benchmark", "finance", "clean72"].map(async (id) => [
      id,
      JSON.parse(
        await readFile(new URL(`../../web/data/${id}.json`, import.meta.url)),
      ),
    ]),
  ),
);
// These fixtures live exclusively in tests and are never exported as benchmark data.
export function completeFixture(source = datasets.insurance) {
  const d = structuredClone(source);
  d.status = "completed";
  d.verification = { status: "verified", test_fixture_only: true };
  for (const [i, c] of d.cases.entries()) {
    const fields = {};
    for (const [id, q] of Object.entries(c.questions)) {
      const keys = Object.keys(q.criteria),
        prediction =
          i === 0 && id === "evidence"
            ? keys.find((k) => k !== c.expected[id])
            : c.expected[id];
      fields[id] = {
        prediction,
        correct: prediction === c.expected[id],
        schema_valid: true,
        probabilities: Object.fromEntries(
          keys.map((k) => [
            k,
            k === prediction ? 0.84 : 0.16 / (keys.length - 1),
          ]),
        ),
      };
    }
    c.result = {
      fields,
      correct: Object.values(fields).every((f) => f.correct),
      schema_valid: true,
      actual_evidence_clauses: c.evidence_options[fields.evidence.prediction],
    };
    c.latency_ms = 1234;
    c.input_tokens = 850;
  }
  return d;
}
export function liveFixture(request) {
  return {
    source: "live_local_inference",
    answers: Object.fromEntries(
      Object.entries(request.questions).map(([id, q]) => [
        id,
        { type: "choice", choice: Object.keys(q.criteria)[0] },
      ]),
    ),
    probabilities_unrounded: Object.fromEntries(
      Object.entries(request.questions).map(([id, q]) => {
        const keys = Object.keys(q.criteria);
        return [
          id,
          Object.fromEntries(
            keys.map((key, i) => [
              key,
              i === 0 ? 0.75 : 0.25 / (keys.length - 1),
            ]),
          ),
        ];
      }),
    ),
    truncated: false,
    input_tokens: 550,
    latency_ms: 1200,
    runtime: {
      backend: "cpu",
      device: "cpu",
      device_name: "Test-only CPU fixture",
      precision: "NF4",
    },
  };
}
export async function harness({
  hash = "#explorer",
  enabled = false,
  insurance,
  requestHandler,
  failFiles = [],
  theme = null,
  storageThrows = false,
  overrides = {},
} = {}) {
  const { document, window: dom } = parseHTML(html),
    listeners = new Map(),
    storage = new Map(theme ? [["clef-theme", theme]] : []),
    calls = [],
    downloads = [];
  // LinkeDOM intentionally lacks the HTMLSelectElement.value setter. Model only
  // that browser primitive, leaving application events/rendering untouched.
  const prototype = Object.getPrototypeOf(document.querySelector("select"));
  if (!Object.getOwnPropertyDescriptor(prototype, "value")?.set)
    Object.defineProperty(prototype, "value", {
      configurable: true,
      get() {
        return (
          [...this.querySelectorAll("option")]
            .find((o) => o.hasAttribute("selected"))
            ?.getAttribute("value") ??
          this.querySelector("option")?.getAttribute("value") ??
          ""
        );
      },
      set(value) {
        for (const option of this.querySelectorAll("option")) {
          if (option.getAttribute("value") === String(value))
            option.setAttribute("selected", "");
          else option.removeAttribute("selected");
        }
      },
    });
  dom.HTMLElement.prototype.focus = function () {
    this.ownerDocument.__focused = this;
  };
  let current = hash,
    index = 0;
  const history = [hash];
  const emit = (name) => (listeners.get(name) || []).forEach((fn) => fn());
  const location = {
    get hash() {
      return current;
    },
    set hash(value) {
      current = value.startsWith("#") ? value : "#" + value;
      history.splice(++index);
      history[index] = current;
      emit("hashchange");
    },
  };
  const win = {
    location,
    history: {
      replaceState(_state, _title, url) {
        current = url;
        history[index] = url;
      },
      back() {
        if (index > 0) {
          current = history[--index];
          emit("popstate");
          emit("hashchange");
        }
      },
      forward() {
        if (index < history.length - 1) {
          current = history[++index];
          emit("popstate");
          emit("hashchange");
        }
      },
    },
    localStorage: {
      getItem(key) {
        if (storageThrows) throw Error("disabled");
        return storage.get(key) || null;
      },
      setItem(key, value) {
        if (storageThrows) throw Error("disabled");
        storage.set(key, value);
      },
    },
    addEventListener(name, fn) {
      listeners.set(name, [...(listeners.get(name) || []), fn]);
    },
    setTimeout() {
      return 1;
    },
    clearTimeout() {},
    URL: {
      createObjectURL(blob) {
        downloads.push(blob);
        return "blob:test";
      },
      revokeObjectURL() {},
    },
    Event: dom.Event,
  };
  const $ = (id) => document.getElementById(id);
  const fetch = async (url, options = {}) => {
    calls.push({ url, options });
    if (url === "/api/health")
      return {
        ok: true,
        json: async () => ({
          inference_enabled: enabled,
          model_loaded: false,
          requested_profile: enabled ? "cpu-nf4" : null,
        }),
      };
    if (url === "/api/infer") {
      if (requestHandler) return requestHandler(JSON.parse(options.body));
      return {
        ok: true,
        json: async () => liveFixture(JSON.parse(options.body)),
      };
    }
    const name = url.split("/").at(-1).replace(".json", "");
    if (failFiles.includes(name)) return { ok: false };
    const value =
      overrides[name] ||
      (name === "insurance" && insurance ? insurance : datasets[name]);
    return { ok: !!value, json: async () => structuredClone(value) };
  };
  const app = createWorkbench({ document, window: win, fetch });
  await app.init();
  const click = (selector) => {
    const el = document.querySelector(selector);
    if (!el) throw Error("Missing " + selector);
    el.dispatchEvent(new dom.Event("click", { bubbles: true }));
    return el;
  };
  const change = (id, value, type = "change") => {
    $(id).value = value;
    $(id).dispatchEvent(new dom.Event(type, { bubbles: true }));
  };
  return {
    app,
    document,
    window: win,
    $,
    click,
    change,
    calls,
    downloads,
    storage,
  };
}
