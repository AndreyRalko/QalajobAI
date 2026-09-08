(function () {
  function getCookie(name) {
    const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? decodeURIComponent(match[2]) : "";
  }

  async function api(path, options = {}) {
    const opts = { credentials: "same-origin", ...options };
    const headers = new Headers(opts.headers || {});
    if (!headers.has("Accept")) headers.set("Accept", "application/json");
    if (!headers.has("Accept-Language") && window.QJ.locale) {
      headers.set("Accept-Language", window.QJ.locale);
    }
    const method = (opts.method || "GET").toUpperCase();
    if (method !== "GET" && method !== "HEAD") {
      const csrf = window.QJ.csrfToken || getCookie("csrftoken");
      if (csrf) headers.set("X-CSRFToken", csrf);
    }
    if (opts.json !== undefined) {
      headers.set("Content-Type", "application/json");
      opts.body = JSON.stringify(opts.json);
      delete opts.json;
    }
    opts.headers = headers;
    const res = await fetch((window.QJ.apiBase || "/api/v1") + path, opts);
    const text = await res.text();
    let data = null;
    try { data = text ? JSON.parse(text) : null; } catch (_) { data = { raw: text }; }
    if (!res.ok) {
      const msg = (data && (data.message || data.detail || data.error)) || res.statusText;
      throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
    }
    return data && Object.prototype.hasOwnProperty.call(data, "data") ? data.data : data;
  }

  window.QJ.api = api;
})();
