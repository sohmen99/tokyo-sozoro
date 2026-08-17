/* 最小限の DOM スタブ。読み込み時の例外と、主要ボタンの動作を実際に走らせて確かめる。 */
const fs = require("fs");
const html = fs.readFileSync("index.html", "utf8");
const markup = html.split("<script>")[0];
const js = html.split("<script>")[1].split("</script>")[0];

const ids = new Set([...markup.matchAll(/id="([^"]+)"/g)].map(m => m[1]));
const listeners = {};           // id -> {event: fn}
const store = {};

function el(id) {
  const e = {
    id, tagName: "DIV", hidden: false, disabled: false, textContent: "", innerHTML: "",
    value: "", scrollTop: 0, offsetHeight: 120, dataset: {}, _attr: {},
    style: new Proxy({ setProperty(){}, removeProperty(){} }, { get:(t,k)=>t[k]??"", set:(t,k,v)=>{t[k]=v;return true} }),
    classList: {
      _s: new Set(),
      add(...c){c.forEach(x=>this._s.add(x))}, remove(...c){c.forEach(x=>this._s.delete(x))},
      toggle(c,f){ f===undefined ? (this._s.has(c)?this._s.delete(c):this._s.add(c)) : (f?this._s.add(c):this._s.delete(c)); },
      contains(c){return this._s.has(c)}
    },
    setAttribute(k,v){ this._attr[k]=String(v); if(k.startsWith("data-")) this.dataset[k.slice(5)]=String(v); },
    getAttribute(k){ return k in this._attr ? this._attr[k] : null; },
    removeAttribute(k){ delete this._attr[k]; },
    addEventListener(ev,fn){ (listeners[id]??={})[ev]=fn; },
    removeEventListener(){}, appendChild(){}, focus(){},
    setPointerCapture(){}, releasePointerCapture(){},
    querySelector(){ return el("?"); }, querySelectorAll(){ return []; },
    closest(){ return null; },
    getBoundingClientRect(){ return {left:0,top:0,width:402,height:874}; },
  };
  return e;
}
const cache = {};
const get = id => (cache[id] ??= el(id));

const list = (sel) => {
  // 実マークアップから件数だけ数えて、その数のスタブを返す
  const n = (sel.includes(".chip") ? (markup.match(/class="chip"/g)||[]).length
          : sel.includes("#seg button") ? (markup.match(/<button aria-pressed/g)||[]).length
          : sel.includes("lang-switch button") ? 2
          : sel.includes("[data-en]") ? 40
          : sel.includes(".mk") ? 21
          : sel.includes("[data-mkx]") ? 21
          : 0);
  const out = [];
  for (let i=0;i<n;i++){ const e = el(sel+"#"+i); e.dataset.lang = i?"en":"ja"; e.dataset.ja="x"; e.dataset.en="x"; e.setAttribute("aria-pressed", i<2?"true":"false"); out.push(e); }
  return out;
};

global.window = {
  addEventListener(){}, removeEventListener(){},
  ResizeObserver: class { observe(){} },
  DeviceOrientationEvent: function(){},
};
global.document = {
  documentElement: el("html"),
  getElementById: (id) => ids.has(id) ? get(id) : (() => { throw new Error("getElementById: 存在しない id → " + id); })(),
  querySelector: (s) => el(s),
  querySelectorAll: list,
  createElement: (t) => el("new:"+t),
  createElementNS: (ns,t) => el("ns:"+t),
  addEventListener(){},
};
global.ResizeObserver = window.ResizeObserver;
global.DeviceOrientationEvent = window.DeviceOrientationEvent;
global.screen = { orientation: { angle: 0 } };
global.navigator = { geolocation: { getCurrentPosition(){}, watchPosition(){return 1}, clearWatch(){} } };
const mem = () => ({ _d:{}, getItem(k){return this._d[k]??null}, setItem(k,v){this._d[k]=String(v)}, removeItem(k){delete this._d[k]} });
global.localStorage = mem(); global.sessionStorage = mem();
global.location = { search: "" };
global.setInterval = () => 0;
global.setTimeout = (fn) => 0;
global.confirm = () => true;
global.alert = () => {};

let ok = true;
try { new Function(js)(); console.log("読み込み: OK（例外なし）"); }
catch (e) { ok = false; console.log("読み込み: 失敗 →", e.message, "\n", e.stack.split("\n").slice(0,4).join("\n")); }

if (ok) {
  const want = [["cover-start","click"],["cover-help","click"],["btn-cover","click"],["btn-start","click"],
                ["btn-back","click"],["btn-hint","click"],["sheet-grip","pointerdown"],["sheet-peek","pointerdown"],
                ["detail-close","click"],["detail-back","click"],["detail-draw","click"],["res-again","click"],
                ["res-home","click"],["btn-settings","click"],["btn-help","click"],
                ["zoom-in","click"],["zoom-out","click"],["locate","click"],
                ["btn-gallery","click"],["gal-back","click"],["res-gallery","click"],
                ["picks-redraw","click"],["picks-cancel","click"],["res-share","click"],["res-keep","click"]];
  const missing = want.filter(([id,ev]) => !listeners[id] || !listeners[id][ev]).map(([id,ev])=>id+":"+ev);
  console.log("クリック待受:", missing.length ? "付いていない → " + missing.join(", ") : "全" + want.length + "個 OK");

  // 実際に押してみる
  const ev = { stopPropagation(){}, preventDefault(){}, target:{closest:()=>null}, currentTarget:{setPointerCapture(){}}, clientX:0, clientY:0, pointerId:1 };
  for (const [id,e] of [["cover-start","click"],["btn-cover","click"],["sheet-grip","pointerdown"],["sheet-grip","pointerup"],
                        ["sheet-peek","pointerdown"],["zoom-in","click"],["zoom-out","click"],["btn-settings","click"],
                        ["btn-help","click"],["res-home","click"],["btn-gallery","click"],["res-gallery","click"],
                        ["picks-cancel","click"],["picks-redraw","click"],["res-share","click"]]) {
    try { listeners[id][e](ev); }
    catch (err) { ok = false; console.log("  " + id + "." + e + " で例外 →", err.message); }
  }
  console.log(ok ? "クリック実行: OK" : "クリック実行: 失敗");
}
process.exit(ok ? 0 : 1);
