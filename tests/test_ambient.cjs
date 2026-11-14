const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('node:assert/strict');
let now = 1000000;
let tick;
let randomValue = 0;
const nodes = [];
const events = {};
const decodes = [];
class Element {
  constructor(tag) { this.tag = tag; this.dataset = {}; this.style = {setProperty(key,value) { this[key] = value; }}; this.children = []; nodes.push(this); }
  appendChild(el) { this.children.push(el); el.parent = this; }
  replaceWith(el) { const i = this.parent.children.indexOf(this); this.parent.children[i] = el; el.parent = this.parent; }
  decode() { return new Promise((resolve, reject) => decodes.push({resolve, reject, node: this})); }
  get textContent() { return this._text; }
  set textContent(value) { this._text = value; this.textWrites = (this.textWrites || 0) + 1; }
  setAttribute(key, value) { this[key] = value; }
  removeAttribute(key) { delete this[key]; }
}
class Media extends Element {}
const video = new Media('video');
video.paused = true; video.ended = false; video.readyState = 4;
const document = {
  readyState: 'complete', body: new Element('body'), head: new Element('head'),
  createElement: tag => new Element(tag), querySelectorAll: () => [video],
  addEventListener: (event, cb) => { events[event] = cb; }
};
const window = { addEventListener: (event, cb) => { events[event] = cb; } }; window.top = window;
class Clock extends Date { constructor(...args) { super(...(args.length ? args : [now])); } static now() { return now; } }
const sandbox = { process: { env: { JETSON_CAST_HOME: '/test-data', JETSON_CAST_NAME: 'Demo Cast', JETSON_CAST_ROTATION: '300' } }, module: { exports: {} }, window, document, Date: Clock, performance: { now: () => now },
  Math: Object.assign(Object.create(Math), {random: () => randomValue}),
  HTMLMediaElement: Media, console, setInterval: cb => { tick = cb; },
  require: name => name === 'fs' ? { readFileSync: file => fs.readFileSync(path.join(__dirname, '../assets', path.basename(file))) } : require(name)
};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../src/ambient.js'), 'utf8'), sandbox);
sandbox.module.exports();
const overlay = nodes.find(n => n.id === 'jetson-ambient');
const art = () => overlay.children.find(n => n.className === 'ja-art');
const pet = nodes.find(n => n.className === 'ja-pet');
const petOpen = nodes.find(n => n.className === 'ja-pet-open');
const petBlink = nodes.find(n => n.className === 'ja-pet-blink');
const petActions = nodes.find(n => n.className === 'ja-pet-actions');
async function flush() { for (const d of decodes.splice(0)) d.resolve(); await Promise.resolve(); await Promise.resolve(); }
async function step() { tick(); await flush(); }
(async () => {
await step(); assert.equal(overlay.hidden, true); assert.equal(art().src, undefined);
now += 15000; await step(); assert.equal(overlay.hidden, false); assert.equal(overlay.dataset.background, 'moonlit-meadow');
assert.ok(art().src.startsWith('data:image/gif;base64,R0lGOD'));
now += 299999; await step(); assert.equal(overlay.dataset.background, 'moonlit-meadow');
now += 1; await step(); assert.equal(overlay.dataset.background, 'aurora-lake');
now += 300000; await step(); assert.equal(overlay.dataset.background, 'golden-coast');
now += 300000; await step(); assert.equal(overlay.dataset.background, 'orbital-dawn');
now += 300000; await step(); assert.equal(overlay.dataset.background, 'moonlit-meadow');
events.play({target:video}); assert.equal(overlay.hidden, true); assert.equal(art().src, undefined);
video.paused = false; now += 600000; await step(); assert.equal(overlay.hidden, true);
video.paused = true; now += 90000; await step(); assert.equal(overlay.hidden, false);
assert.equal(pet.hidden, true);
now += 14999; await step(); assert.equal(pet.hidden, true);
now += 1; await step(); assert.equal(pet.hidden, false);
assert.equal(pet.dataset.action, 'walk-right');
assert.ok(petActions.style.backgroundImage.startsWith('url("data:image/png;base64,iVBOR'));
now += 15000; await step(); assert.equal(pet.hidden, true); assert.equal(petOpen.src, undefined);
now += 44999; await step(); assert.equal(pet.hidden, true);
now += 1; await step(); assert.equal(pet.hidden, false);
assert.equal(pet.dataset.action, 'walk-left', 'do not repeat consecutive actions');
events.loadstart({target:video});
assert.equal(overlay.hidden, true); assert.equal(pet.hidden, true);
assert.equal(petOpen.src, undefined); assert.equal(petBlink.src, undefined);
assert.equal(petActions.style.backgroundImage, '');
now += 90000; await step(); now += 15000; await step(); assert.equal(pet.hidden, false);
events.play({target:video}); assert.equal(pet.hidden, true); assert.equal(art().src, undefined);
video.paused = false; now += 600000; await step(); assert.equal(pet.hidden, true);
video.paused = true; now += 90000; await step();
events.pointerdown(); assert.equal(overlay.hidden, true); assert.equal(art().src, undefined);
assert.equal(pet.hidden, true); assert.equal(petOpen.src, undefined);
assert.equal(nodes.find(n => n.className === 'ja-name').textContent, 'Demo Cast');
assert.equal(nodes.some(n => n.className === 'ja-status'), false);
assert.equal(nodes.find(n => n.className === 'ja-instruction').textContent, 'Open YouTube on your phone · Tap Cast · Choose Demo Cast');
// Exercise every visit type and ensure playback cleans up all artwork.
const modes = ['walk-right','walk-left','peek-left','peek-right','peek-top','peek-bottom'];
for (const wanted of modes) {
  if (pet.dataset.action === wanted) continue;
  const eligible = modes.filter(mode => mode !== pet.dataset.action);
  randomValue = (eligible.indexOf(wanted) + .1) / eligible.length;
  now += 90000; await step(); now += 25000; await step();
  assert.equal(pet.dataset.action, wanted);
  assert.equal(pet.hidden, false);
  if (wanted.startsWith('walk')) assert.ok(petActions.style.backgroundImage.includes('data:image/png;base64,'));
  else { assert.ok(petOpen.src.startsWith('data:image/png;base64,')); assert.ok(petBlink.src.startsWith('data:image/png;base64,')); }
  events.play({target:video});
  assert.equal(pet.hidden, true); assert.equal(petActions.style.backgroundImage, '');
  assert.equal(petOpen.src, undefined); assert.equal(petBlink.src, undefined);
}
// A decode finishing after casting starts must not paint a late image.
now += 90000; tick(); assert.equal(decodes.length, 1);
events.play({target:video}); await flush();
assert.equal(overlay.hidden, true); assert.equal(art().src, undefined);
// A slow or failed rotation keeps the current image; it never clears the screen.
now += 90000; await step(); const previous = art().src;
now += 300000; tick(); assert.equal(art().src, previous);
assert.equal(decodes.length, 1); decodes.shift().reject(new Error('decode test'));
await Promise.resolve(); await Promise.resolve();
assert.equal(art().src, previous);
const clockNode = nodes.find(n => n.className === 'ja-time');
const clockWrites = clockNode.textWrites;
await step(); await step();
assert.equal(clockNode.textWrites, clockWrites, 'unchanged clock must not rewrite the DOM');
console.log('PASS: rotation, mascot, dismissal, text cleanup, decoded swaps, failure retention, late-decode cancellation, and no redundant clock writes.');

})().catch(error => { console.error(error); process.exitCode = 1; });
