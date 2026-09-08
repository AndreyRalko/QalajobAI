(function () {
  const KEY = "qalajob:vacancy-context";

  function buildDescription(v) {
    const parts = [];
    if (v.city || v.area) parts.push("Город: " + (v.city || v.area));
    if (v.salary) parts.push("Зарплата: " + v.salary);
    if (v.requirement) parts.push("Требования: " + v.requirement);
    if (v.responsibility) parts.push("Обязанности: " + v.responsibility);
    if (v.description && !v.requirement && !v.responsibility) {
      parts.push(v.description);
    } else if (v.description && v.description.length > 40) {
      // keep full description if rich
      if (!parts.some((p) => p.includes(v.description.slice(0, 40)))) {
        parts.push(v.description);
      }
    }
    if (v.url) parts.push("Ссылка: " + v.url);
    return parts.filter(Boolean).join("\n\n");
  }

  function toContext(v) {
    const title = (v.title || v.name || "").trim();
    return {
      id: v.id || null,
      hh_id: String(v.hh_id || v.id || ""),
      jobTitle: title,
      company: (v.company || "").trim(),
      jobDescription: (v.description || "").trim() || buildDescription(v),
      city: v.city || v.area || "",
      salary: v.salary || "",
      url: v.url || "",
    };
  }

  function saveLocal(ctx) {
    try {
      sessionStorage.setItem(KEY, JSON.stringify(ctx));
      localStorage.setItem(KEY, JSON.stringify(ctx));
    } catch (_) { /* ignore */ }
  }

  function loadLocal() {
    try {
      const raw = sessionStorage.getItem(KEY) || localStorage.getItem(KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      if (!parsed || !parsed.jobTitle) return null;
      return parsed;
    } catch (_) {
      return null;
    }
  }

  function clearLocal() {
    try {
      sessionStorage.removeItem(KEY);
      localStorage.removeItem(KEY);
    } catch (_) { /* ignore */ }
  }

  window.QJ = window.QJ || {};
  window.QJ.vacancy = {
    buildDescription,
    toContext,
    saveLocal,
    loadLocal,
    clearLocal,
    async saveToServer(payload, select) {
      const body = {
        hh_id: String(payload.hh_id || payload.id || ""),
        title: payload.title || payload.name || payload.jobTitle || "",
        company: payload.company || "",
        city: payload.city || payload.area || "",
        salary: payload.salary || "",
        url: payload.url || "",
        description:
          payload.description ||
          buildDescription(payload) ||
          payload.jobDescription ||
          "",
        requirement: payload.requirement || "",
        responsibility: payload.responsibility || "",
        select: !!select,
      };
      return window.QJ.api("/hh-saved/", { method: "POST", json: body });
    },
    async list() {
      const data = await window.QJ.api("/hh-saved/");
      return Array.isArray(data) ? data : [];
    },
    async selected() {
      return window.QJ.api("/hh-saved/selected/");
    },
    async select(id) {
      return window.QJ.api("/hh-saved/" + id + "/select/", { method: "POST" });
    },
    async remove(id) {
      return window.QJ.api("/hh-saved/" + id + "/", { method: "DELETE" });
    },
    async clearSelected() {
      return window.QJ.api("/hh-saved/clear-selected/", { method: "POST" });
    },
  };
})();
