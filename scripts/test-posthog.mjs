import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";
import { runInThisContext } from "node:vm";

import { initPosthogIdentity } from "../frontend/src/js/modules/posthog-identity.js";
import { initPosthogCtas } from "../frontend/src/js/modules/posthog-ctas.js";
import { sanitizePosthogEvent } from "../frontend/src/js/modules/posthog-privacy.js";
import { initPosthog } from "../frontend/src/js/modules/posthog.js";

const snippet = readFileSync(new URL("../frontend/templates/components/posthog.html", import.meta.url), "utf8");
const loadedBody = snippet.match(/loaded: function \(instance\) \{([\s\S]*?)\n {6}\},/)[1];
const sdkLoaded = runInThisContext(`(function (instance) {${loadedBody}})`);

function browser(cookie, identity = "") {
  const cookies = new Map(cookie ? [["analytics_consent", cookie]] : []);
  const listeners = {};
  const windowListeners = {};
  const captures = [];
  const identities = [];
  let optedOut = true;
  let distinctId = "anonymous-visitor";
  globalThis.document = {
    body: {
      dataset: { posthogPageviewEnabled: "true", posthogRoute: "/", posthogContentGroup: "marketing" },
      addEventListener() {},
    },
    referrer: "https://example.org/article?private=value",
    addEventListener(name, callback) { listeners[name] = callback; },
    get cookie() { return [...cookies].map(([k, v]) => `${k}=${v}`).join("; "); },
    set cookie(value) {
      const [pair] = value.split(";");
      const [key, ...rest] = pair.split("=");
      if (value.includes("Max-Age=0")) cookies.delete(key);
      else cookies.set(key, rest.join("="));
    },
  };
  globalThis.window = {
    URL,
    location: { protocol: "https:", origin: "https://example.com", pathname: "/", search: "?utm_source=test&token=private" },
    addEventListener(name, callback) { windowListeners[name] = callback; },
    dispatchEvent(event) { windowListeners[event.type]?.(event); },
    SaasAnalytics: { environment: "test", eventPrefix: "built_with_bend", identity: { distinctId: identity } },
    posthog: {
      clear_opt_in_out_capturing() { optedOut = false; },
      get_distinct_id() { return distinctId; },
      identify(id) { distinctId = id; identities.push(id); },
      setPersonProperties() {},
      capture(event, properties) {
        assert.equal(optedOut, false);
        captures.push(sanitizePosthogEvent({ event, properties }));
      },
    },
  };
  return { cookies, captures, identities, listeners };
}

for (const cookie of ["", "granted", "denied"]) {
  test(`pageviews and CTAs start without interaction (legacy choice: ${cookie || "none"})`, async () => {
    const state = browser(cookie);
    // A fresh pageview module models a full page load in each browser.
    const { initPosthogPageviews } = await import(`../frontend/src/js/modules/posthog-pageviews.js?case=${cookie}`);
    sdkLoaded(window.posthog);
    initPosthogIdentity();
    initPosthogPageviews();
    initPosthogCtas();
    assert.equal(state.cookies.has("analytics_consent"), false);
    assert.equal(state.captures.filter((e) => e.event === "$pageview").length, 1);
    assert.equal(state.captures[0].properties.$current_url, "https://example.com/");
    assert.equal(state.captures[0].properties.utm_source, "test");
    assert.equal(state.captures[0].properties.$referrer, "https://example.org");
    assert.deepEqual(state.identities, []);
    assert.ok(state.cookies.has("marketing_attribution"));
    state.listeners.click({ target: { closest: () => ({ href: "/accounts/signup/?secret=private", dataset: { posthogCta: "signup", posthogCtaLocation: "header" } }) } });
    assert.equal(state.captures[1].event, "built_with_bend_marketing_cta_clicked");
    assert.equal(state.captures[1].properties.destination, "/accounts/signup/");
    assert.equal(JSON.stringify(state.captures).includes("private"), false);
  });
}

test("signed-in identity is linked automatically and logout still resets it", () => {
  const state = browser("denied", "42");
  let resets = 0;
  window.posthog.reset = () => { resets++; };
  initPosthog();
  assert.deepEqual(state.identities, []);
  assert.deepEqual(state.captures, []);
  sdkLoaded(window.posthog);
  initPosthog(); // Repeated startup must not duplicate identity or the initial pageview.
  assert.deepEqual(state.identities, ["42"]);
  assert.equal(state.captures.filter((e) => e.event === "$pageview").length, 1);
  state.listeners.submit({ target: { matches: () => true } });
  assert.equal(resets, 1);
});

test("private routes stay excluded and no-key pages remain functional", async () => {
  const state = browser("");
  document.body.dataset = {};
  const { initPosthogPageviews } = await import("../frontend/src/js/modules/posthog-pageviews.js?case=private");
  initPosthogIdentity();
  initPosthogPageviews();
  assert.deepEqual(state.captures, []);
  delete window.SaasAnalytics;
  delete window.posthog;
  assert.doesNotThrow(() => initPosthog());
});
