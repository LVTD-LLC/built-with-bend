// Identity comes only from published-object view context, never the browser URL.
const definitions = {
  project: { route: "/projects/:slug/", path: /^\/projects\/[a-z0-9][a-z0-9_-]*\/$/i },
  article: { route: "/blog/:slug", path: /^\/blog\/[a-z0-9][a-z0-9_-]*$/i },
};

export function publicContentProperties(context = window.SaasAnalytics?.pageviewContext) {
  const definition = Object.hasOwn(definitions, context?.publicContentType)
    ? definitions[context.publicContentType] : null;
  const path = context?.publicContentPath;
  if (!context?.enabled || !definition || context.route !== definition.route ||
      typeof path !== "string" || path.length > 200 || !definition.path.test(path)) return {};
  // Legacy UUID aliases and numeric identifiers are not public content identities.
  const slug = path.split("/")[2];
  if (/^\d+$/.test(slug) || /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i.test(slug)) return {};
  return { public_content_path: path, public_content_type: context.publicContentType };
}

export function initPosthogOutbound() {
  document.addEventListener("click", (event) => {
    const element = event.target.closest?.("a[data-posthog-outbound]");
    const kind = element?.dataset.posthogOutbound;
    const content = publicContentProperties();
    if (content.public_content_type !== "project" || !content.public_content_path || !["website", "repository", "source"].includes(kind)) return;
    window.posthog?.capture?.("built_with_bend_project_outbound_clicked", {
      ...content,
      destination_kind: kind,
      environment: window.SaasAnalytics?.environment || "unknown",
      event_version: 1,
    });
  });
}
