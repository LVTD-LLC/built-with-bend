import { initPosthogIdentity } from "./posthog-identity.js";
import { initPosthogCtas } from "./posthog-ctas.js";
import { initPosthogPageviews } from "./posthog-pageviews.js";

export function initPosthog() {
  const analytics = window.SaasAnalytics;
  if (!analytics) return;
  if (!analytics.ready) {
    window.addEventListener("saas:analytics-ready", initPosthog, { once: true });
    return;
  }
  if (analytics.initialized) return;
  analytics.initialized = true;
  initPosthogIdentity();
  initPosthogCtas();
  initPosthogPageviews();

  document.addEventListener("submit", (event) => {
    if (event.target.matches("form[data-posthog-reset]")) {
      window.posthog?.reset?.();
    }
  });
}
