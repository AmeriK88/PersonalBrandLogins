// Run with: node --test tests_js
// Uses a minimal fake DOM; it checks the control logic, not real iPhone Safari behaviour.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const read = (name) => fs.readFileSync(path.join(__dirname, '..', 'static', 'js', 'core', name), 'utf8');

class FakeNode {
  constructor(id, tag = 'div') {
    this.id = id;
    this.tagName = tag.toUpperCase();
    this.listeners = {};
    this.attrs = {};
    this.dataset = {};
    this.style = {};
    this.classes = new Set();
    this.children = [];
    this.textContent = '';
    this.paused = true;
    this.ended = false;
    this.muted = false;
    this.currentTime = 0;
    this.playCalls = 0;
    this.pauseCalls = 0;
    this.playImpl = () => Promise.resolve();
    this.classList = {
      add: (...c) => c.forEach((x) => this.classes.add(x)),
      remove: (...c) => c.forEach((x) => this.classes.delete(x)),
    };
  }
  addEventListener(type, fn, capture) { if (capture === true && type === 'error') this.captureErrorListener = true; (this.listeners[type] ||= []).push(fn); }
  removeEventListener(type, fn) { this.listeners[type] = (this.listeners[type] || []).filter((f) => f !== fn); }
  setAttribute(k, v) { this.attrs[k] = String(v); }
  getAttribute(k) { return k in this.attrs ? this.attrs[k] : null; }
  contains(n) { return n === this; }
  dispatch(type, extra = {}) {
    const event = { type, target: extra.target || this, currentTarget: this, ...extra };
    (this.listeners[type] || []).slice().forEach((fn) => fn(event));
    return event;
  }
  querySelectorAll() { return this.children; }
  play() {
    this.playCalls += 1;
    return this.playImpl();
  }
  pause() {
    this.pauseCalls += 1;
    if (!this.paused) { this.paused = true; this.dispatch('pause'); }
  }
}

function setup({ withReel = false, ua = 'iPhone', videoCount = 1, search = '' } = {}) {
  const audio = new FakeNode('about-narration', 'audio');
  audio.playImpl = () => { audio.paused = false; audio.dispatch('play'); audio.dispatch('playing'); return Promise.resolve(); };
  const btn = new FakeNode('about-audio-toggle', 'button');
  const nodes = { 'about-narration': audio, 'about-audio-toggle': btn };
  const document = new FakeNode('document');
  document.readyState = 'complete';
  document.hidden = false;
  document.getElementById = (id) => nodes[id] || null;
  document.createElement = (tag) => new FakeNode('', tag);
  const holder = new FakeNode('holder');
  holder.insertBefore = () => { holder.insertedInto = true; };
  btn.parentNode = holder;
  let reel = null;
  const videos = [];
  if (withReel) {
    reel = new FakeNode('recovery-reel');
    reel.attrs['data-sync-audio'] = 'about-narration';
    for (let i = 0; i < videoCount; i += 1) videos.push(new FakeNode(`v${i}`, 'video'));
    reel.children = [new FakeNode('img', 'img'), ...videos];
    nodes['recovery-reel'] = reel;
  }
  const context = {
    document,
    Node: FakeNode,
    navigator: { userAgent: ua },
    window: { setTimeout: () => 1, clearTimeout() {}, location: { search }, navigator: { serviceWorker: { controller: null } } },
    URLSearchParams,
    console: { warn() {}, info() {} },
    Number, Array, Promise,
  };
  vm.createContext(context);
  vm.runInContext(read('blog-audio.js'), context);
  if (withReel) vm.runInContext(read('recovery-reel.js'), context);
  return { audio, btn, document, reel, videos, holder };
}

test('initial state is paused with no autoplay or document click listener', () => {
  const { audio, btn, document } = setup();
  assert.equal(audio.playCalls, 0);
  assert.equal(audio.muted, false);
  assert.equal(btn.getAttribute('aria-pressed'), 'false');
  assert.match(btn.textContent, /Play Narration/);
  assert.equal((document.listeners.click || []).length, 0);
});

test('first click starts audible narration, second click pauses', () => {
  const { audio, btn } = setup();
  btn.dispatch('click');
  assert.equal(audio.playCalls, 1);
  assert.equal(audio.muted, false);
  assert.equal(btn.getAttribute('aria-pressed'), 'true');
  assert.match(btn.textContent, /Pause Narration/);
  btn.dispatch('click');
  assert.equal(audio.pauseCalls, 1);
  assert.equal(btn.getAttribute('aria-pressed'), 'false');
  assert.match(btn.textContent, /Play Narration/);
});

test('rejected play() leaves the button in the paused state', async () => {
  const { audio, btn } = setup();
  audio.playImpl = () => Promise.reject(new Error('NotAllowedError'));
  btn.dispatch('click');
  await new Promise((r) => setImmediate(r));
  assert.equal(btn.getAttribute('aria-pressed'), 'false');
  assert.match(btn.textContent, /Play Narration/);
});

test('synchronous play() throw is handled', () => {
  const { audio, btn } = setup();
  audio.playImpl = () => { throw new Error('boom'); };
  assert.doesNotThrow(() => btn.dispatch('click'));
  assert.equal(btn.getAttribute('aria-pressed'), 'false');
});

test('ended resets the button and narration can restart', () => {
  const { audio, btn } = setup();
  btn.dispatch('click');
  audio.paused = true; audio.ended = true;
  audio.dispatch('ended');
  assert.equal(btn.getAttribute('aria-pressed'), 'false');
  btn.dispatch('click');
  assert.equal(audio.playCalls, 2);
  assert.equal(btn.getAttribute('aria-pressed'), 'true');
});

test('error event resets the button', () => {
  const { audio, btn } = setup();
  btn.dispatch('click');
  audio.dispatch('error');
  assert.equal(btn.getAttribute('aria-pressed'), 'false');
});

test('hiding the page pauses playing narration and updates the button', () => {
  const { audio, btn, document } = setup();
  btn.dispatch('click');
  document.hidden = true;
  document.dispatch('visibilitychange');
  assert.equal(audio.paused, true);
  assert.equal(btn.getAttribute('aria-pressed'), 'false');
});

test('clicking elsewhere never starts or unmutes narration', () => {
  const { audio, document } = setup();
  document.dispatch('click', { target: new FakeNode('other') });
  assert.equal(audio.playCalls, 0);
});

test('narration button click does not trigger reel video unlocking', () => {
  const { audio, btn, document, videos } = setup({ withReel: true });
  btn.dispatch('click');
  document.dispatch('click', { target: btn });
  assert.equal(audio.playCalls, 1);
  assert.equal(videos[0].playCalls, 0);
});

test('first non-narration gesture still unlocks reel videos on iOS, once', () => {
  const { btn, document, videos } = setup({ withReel: true });
  btn.dispatch('click');
  document.dispatch('click', { target: btn });
  document.dispatch('click', { target: new FakeNode('page') });
  assert.equal(videos[0].playCalls, 1);
  document.dispatch('click', { target: new FakeNode('page') });
  assert.equal(videos[0].playCalls, 1);
});

test('reel sync reacts to narration pause without touching narration', () => {
  const { audio, btn, videos } = setup({ withReel: true, ua: 'Desktop' });
  btn.dispatch('click');
  btn.dispatch('click');
  assert.equal(audio.playCalls, 1);
  assert.equal(audio.pauseCalls, 1);
  assert.ok(videos[0].pauseCalls > 0);
});

test('capture-phase error listener catches <source> failures and resets the button', () => {
  const { audio, btn } = setup();
  btn.dispatch('click');
  assert.equal(audio.captureErrorListener, true);
  audio.dispatch('error');
  assert.equal(btn.getAttribute('aria-pressed'), 'false');
  assert.equal(btn.dataset.narrationError, 'media-error');
});

test('failed playback records a diagnostic without exposing it in the UI text', async () => {
  const { audio, btn } = setup();
  audio.playImpl = () => Promise.reject(Object.assign(new Error('x'), { name: 'NotAllowedError' }));
  btn.dispatch('click');
  await new Promise((r) => setImmediate(r));
  assert.equal(btn.dataset.narrationError, 'play-rejected');
  assert.doesNotMatch(btn.textContent, /NotAllowed|error/i);
});

test('diagnostic mode is off by default and enables native controls only with ?narration_debug=1', () => {
  const normal = setup();
  assert.notEqual(normal.audio.controls, true);
  assert.equal(normal.holder.insertedInto, undefined);
  const debug = setup({ search: '?narration_debug=1' });
  assert.equal(debug.audio.controls, true);
  assert.equal(debug.audio.preload, 'metadata');
  assert.ok(debug.holder.insertedInto);
});

test('service worker bypasses media and Range requests and uses a bumped cache version', () => {
  const src = fs.readFileSync(path.join(__dirname, '..', 'templates', 'service-worker.js'), 'utf8')
    .replace(/{% load[^%]*%}/g, '').replace(/{%[^%]*%}/g, 'x');
  const handlers = {};
  const fetched = [];
  const sw = {
    addEventListener: (t, fn) => { handlers[t] = fn; },
    skipWaiting() {}, clients: { claim() {} },
    location: { origin: 'https://site.test' },
  };
  vm.runInNewContext(src, { self: sw, caches: { open: async () => ({ addAll: async () => {}, put: async () => {} }), keys: async () => [], match: async () => undefined }, fetch: (r) => { fetched.push(r); return Promise.resolve({ clone: () => ({}) }); }, URL, Promise });
  assert.match(src, /CACHE_VERSION = 'v(\d+)'/);
  assert.ok(Number(/CACHE_VERSION = 'v(\d+)'/.exec(src)[1]) >= 4);

  const run = (req) => {
    let responded = false;
    handlers.fetch({ request: req, respondWith: () => { responded = true; } });
    return responded;
  };
  const make = (url, extra = {}) => ({ url, method: 'GET', mode: 'no-cors', destination: '', headers: { has: (h) => Boolean(extra.range) && h === 'range', get: () => '' }, ...extra });
  assert.equal(run(make('https://res.cloudinary.com/demo/video/upload/blog/narration/n_abc', { destination: 'audio' })), false);
  assert.equal(run(make('https://site.test/static/audio/narration.mp3')), false);
  assert.equal(run(make('https://site.test/x', { range: true })), false);
  assert.equal(run(make('https://site.test/static/js/core/blog-audio.js')), true);
});