/*
 * toshin-web-tools / tool-helpers.js
 *
 * 新規ツール本体用の共通 JS。IIFE で window.toshin namespace に export する。
 * 既存 32 ツールには注入しない。新規ツール作成時に
 *   <script src="../../assets/tool-helpers.js"></script>
 * で参照する。
 *
 * 提供:
 *  - Slider:   <input type="range"> + 表示ラベル(<span data-bind="ID">)の双方向同期
 *  - ToolState: 単純な reactive state(set / subscribe)
 *  - RAFLoop:  fixed-step requestAnimationFrame ループ
 *  - 数値:     clamp / map / linspace / formatNumber
 *  - SVG:      svgEl(tag, attrs, children) / svgPath(points, close)
 */

(function (window) {
  "use strict";

  // ---------------- Number helpers ----------------
  function clamp(x, lo, hi) { return Math.min(Math.max(x, lo), hi); }
  function map(x, a, b, c, d) {
    if (a === b) return c; // guard: 縮退区間ではターゲット下限を返す(0 除算防止)
    return c + (d - c) * (x - a) / (b - a);
  }
  function linspace(a, b, n) {
    if (n < 2) return [a];
    const out = new Array(n);
    const step = (b - a) / (n - 1);
    for (let i = 0; i < n; i++) out[i] = a + step * i;
    return out;
  }
  function formatNumber(x, digits = 3) {
    if (!Number.isFinite(x)) return String(x);
    if (Math.abs(x) < 1e-3 && x !== 0) return x.toExponential(2);
    if (Math.abs(x) >= 1e4) return x.toExponential(2);
    return Number.parseFloat(x.toFixed(digits)).toString();
  }

  // ---------------- Slider wrapper ----------------
  // <div class="tool-slider">
  //   <label>η = <span class="tool-slider-value" data-bind="eta"></span></label>
  //   <input id="eta" type="range" min="0" max="1" step="0.01" value="0.05">
  // </div>
  // const eta = new toshin.Slider('eta').onChange(v => updateViz());
  class Slider {
    constructor(inputId, opts = {}) {
      const input = document.getElementById(inputId);
      if (!input) throw new Error(`Slider: input not found: #${inputId}`);
      this.input = input;
      this.format = opts.format || ((v) => formatNumber(v));
      this.valueEl = document.querySelector(`[data-bind="${inputId}"]`);
      this.listeners = [];
      input.addEventListener("input", () => this._emit());
      this._render();
    }
    get value() { return parseFloat(this.input.value); }
    set value(v) { this.input.value = String(v); this._render(); this._emit(); }
    onChange(fn) { this.listeners.push(fn); return this; }
    _render() {
      if (this.valueEl) this.valueEl.textContent = this.format(this.value);
    }
    _emit() {
      this._render();
      for (const fn of this.listeners) fn(this.value);
    }
  }

  // ---------------- ToolState (pub/sub) ----------------
  class ToolState {
    constructor(initial = {}) {
      this._state = { ...initial };
      this._listeners = [];
    }
    get state() { return this._state; }
    set(update) {
      const changed = {};
      let any = false;
      for (const k of Object.keys(update)) {
        if (this._state[k] !== update[k]) {
          this._state[k] = update[k];
          changed[k] = update[k];
          any = true;
        }
      }
      if (any) for (const fn of this._listeners) fn(this._state, changed);
    }
    subscribe(fn) {
      this._listeners.push(fn);
      return () => { this._listeners = this._listeners.filter((f) => f !== fn); };
    }
  }

  // ---------------- RAFLoop (fixed-step) ----------------
  // tab 非表示中は raf が止まり、復帰時に巨大 dt が来る。
  // dt を maxDt(既定 100ms)で clamp し、visibilitychange でも累積をリセットする。
  class RAFLoop {
    constructor(stepFn, opts = {}) {
      this.stepFn = stepFn;
      this.fps = opts.fps || 60;
      this.maxDt = opts.maxDt != null ? opts.maxDt : 100; // ms
      this.running = false;
      this._raf = null;
      this._lastT = 0;
      this._accum = 0;
      this._onVisibility = () => {
        if (document.visibilityState === "visible") {
          this._lastT = performance.now();
          this._accum = 0;
        }
      };
    }
    start() {
      if (this.running) return;
      this.running = true;
      this._lastT = performance.now();
      this._accum = 0;
      document.addEventListener("visibilitychange", this._onVisibility);
      const tick = (now) => {
        if (!this.running) return;
        let dt = now - this._lastT;
        if (dt > this.maxDt) dt = this.maxDt; // clamp: 復帰時の巨大 dt を抑える
        this._lastT = now;
        const targetMs = 1000 / this.fps;
        this._accum += dt;
        let safety = 8;
        while (this._accum >= targetMs && safety-- > 0) {
          this.stepFn(targetMs / 1000);
          this._accum -= targetMs;
        }
        this._raf = requestAnimationFrame(tick);
      };
      this._raf = requestAnimationFrame(tick);
    }
    stop() {
      this.running = false;
      if (this._raf) cancelAnimationFrame(this._raf);
      this._raf = null;
      document.removeEventListener("visibilitychange", this._onVisibility);
    }
    toggle() { this.running ? this.stop() : this.start(); }
  }

  // ---------------- SVG helpers ----------------
  const SVG_NS = "http://www.w3.org/2000/svg";
  function svgEl(tag, attrs = {}, children = []) {
    const el = document.createElementNS(SVG_NS, tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v == null) continue;
      el.setAttribute(k, String(v));
    }
    for (const c of children) {
      if (c == null) continue;
      if (typeof c === "string") el.appendChild(document.createTextNode(c));
      else el.appendChild(c);
    }
    return el;
  }
  function svgPath(points, close = false) {
    if (!points.length) return "";
    let d = `M ${points[0][0]} ${points[0][1]}`;
    for (let i = 1; i < points.length; i++) {
      d += ` L ${points[i][0]} ${points[i][1]}`;
    }
    if (close) d += " Z";
    return d;
  }

  // ---------------- export ----------------
  window.toshin = window.toshin || {};
  Object.assign(window.toshin, {
    Slider,
    ToolState,
    RAFLoop,
    clamp, map, linspace, formatNumber,
    svgEl, svgPath,
  });
})(window);
