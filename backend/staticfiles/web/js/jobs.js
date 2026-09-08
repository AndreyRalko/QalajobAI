(function () {
  const form = document.getElementById("jobsForm");
  if (!form || !window.QJ || !window.QJ.api || !window.QJ.vacancy) return;

  const list = document.getElementById("jobsList");
  const status = document.getElementById("jobsStatus");
  const savedList = document.getElementById("savedList");
  const savedEmpty = document.getElementById("savedEmpty");
  const t = () => window.QJ.i18n || {};

  function esc(text) {
    return String(text || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function normalizeRec(job) {
    const v = job.vacancy || job;
    return {
      hh_id: String(v.id || job.vacancy_id || job.hh_id || ""),
      title: v.name || v.title || "",
      company: v.company || (v.employer && v.employer.name) || "",
      city: typeof v.area === "string" ? v.area : (v.area && v.area.name) || v.city || "",
      salary: v.salary || "",
      url: v.url || v.alternate_url || (job.vacancy_id ? "https://hh.kz/vacancy/" + job.vacancy_id : ""),
      requirement: v.requirement || "",
      responsibility: v.responsibility || "",
      description: v.description || "",
      explanation: job.explanation || "",
      match_score: job.match_score,
    };
  }

  function renderCard(item, opts) {
    opts = opts || {};
    const title = item.title || item.name || "";
    if (!title) return null;
    const meta = [item.company, item.city, item.salary].filter(Boolean).join(" · ");
    const card = document.createElement("article");
    card.className = "job-card card" + (item.is_selected ? " is-selected" : "");
    const actions = document.createElement("div");
    actions.className = "job-actions";

    const html =
      "<h3>" +
      esc(title) +
      (item.is_selected
        ? ' <span class="badge-selected">' + esc(t().selectedForAi || "Selected") + "</span>"
        : "") +
      "</h3>" +
      (meta ? "<p>" + esc(meta) + "</p>" : "") +
      (typeof item.match_score === "number"
        ? "<p>" + esc(String(item.match_score)) + "%</p>"
        : "") +
      (item.explanation ? "<p>" + esc(item.explanation) + "</p>" : "");
    card.innerHTML = html;

    if (item.url) {
      const a = document.createElement("a");
      a.href = item.url;
      a.target = "_blank";
      a.rel = "noopener";
      a.textContent = t().openOnHh || "hh.kz";
      actions.appendChild(a);
    }

    if (opts.showSave !== false) {
      const saveBtn = document.createElement("button");
      saveBtn.type = "button";
      saveBtn.className = "btn btn-sm btn-ghost";
      saveBtn.textContent = t().saveVacancy || "Save";
      saveBtn.addEventListener("click", async () => {
        saveBtn.disabled = true;
        try {
          await window.QJ.vacancy.saveToServer(item, false);
          saveBtn.textContent = t().savedVacancy || "Saved";
          await refreshSaved();
        } catch (err) {
          alert((t().errorPrefix || "Error") + ": " + err.message);
          saveBtn.disabled = false;
        }
      });
      actions.appendChild(saveBtn);
    }

    if (opts.showSelect) {
      const selBtn = document.createElement("button");
      selBtn.type = "button";
      selBtn.className = "btn btn-sm";
      selBtn.textContent = item.is_selected
        ? t().selectedForAi || "Selected"
        : t().useForAi || "Use for AI";
      selBtn.disabled = !!item.is_selected;
      selBtn.addEventListener("click", async () => {
        try {
          const updated = await window.QJ.vacancy.select(item.id);
          const ctx = window.QJ.vacancy.toContext(updated);
          window.QJ.vacancy.saveLocal(ctx);
          await refreshSaved();
        } catch (err) {
          alert((t().errorPrefix || "Error") + ": " + err.message);
        }
      });
      actions.appendChild(selBtn);
    }

    if (opts.showPrepare) {
      const prepBtn = document.createElement("button");
      prepBtn.type = "button";
      prepBtn.className = "btn btn-sm";
      prepBtn.textContent = t().prepareWithAi || "Prepare with AI";
      prepBtn.addEventListener("click", async () => {
        prepBtn.disabled = true;
        try {
          const saved = await window.QJ.vacancy.saveToServer(item, true);
          const ctx = window.QJ.vacancy.toContext(saved);
          window.QJ.vacancy.saveLocal(ctx);
          window.location.href =
            window.QJ.workspaceResumeUrl || "/app/student/ai/resume/";
        } catch (err) {
          alert((t().errorPrefix || "Error") + ": " + err.message);
          prepBtn.disabled = false;
        }
      });
      actions.appendChild(prepBtn);
    }

    if (opts.showRemove && item.id) {
      const delBtn = document.createElement("button");
      delBtn.type = "button";
      delBtn.className = "btn btn-sm btn-danger";
      delBtn.textContent = t().unsaveVacancy || "Remove";
      delBtn.addEventListener("click", async () => {
        try {
          await window.QJ.vacancy.remove(item.id);
          if (item.is_selected) window.QJ.vacancy.clearLocal();
          await refreshSaved();
        } catch (err) {
          alert((t().errorPrefix || "Error") + ": " + err.message);
        }
      });
      actions.appendChild(delBtn);
    }

    card.appendChild(actions);
    return card;
  }

  async function refreshSaved() {
    if (!savedList) return;
    savedList.innerHTML = "";
    try {
      const items = await window.QJ.vacancy.list();
      if (savedEmpty) savedEmpty.style.display = items.length ? "none" : "block";
      items.forEach((item) => {
        const card = renderCard(item, {
          showSave: false,
          showSelect: true,
          showPrepare: true,
          showRemove: true,
        });
        if (card) savedList.appendChild(card);
      });
      const selected = items.find((x) => x.is_selected);
      if (selected) {
        window.QJ.vacancy.saveLocal(window.QJ.vacancy.toContext(selected));
      }
    } catch (err) {
      if (savedEmpty) {
        savedEmpty.style.display = "block";
        savedEmpty.textContent = (t().errorPrefix || "Error") + ": " + err.message;
      }
    }
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const interests = document.getElementById("interests").value.trim();
    if (!interests) return;
    status.textContent = t().lookingJobs || "Searching…";
    list.innerHTML = "";
    try {
      const data = await window.QJ.api("/ai/job-recommendations/", {
        method: "POST",
        json: {
          job_interests: interests,
          language: window.QJ.locale || "kk",
          limit: 10,
        },
      });
      const jobs =
        (data && (data.recommendations || data.jobs || data.items)) || [];
      if (!jobs.length) {
        status.textContent = t().tryOtherQuery || "Nothing found.";
        return;
      }
      status.textContent = (t().found || "Found") + ": " + jobs.length;
      jobs.forEach((job) => {
        const item = normalizeRec(job);
        const card = renderCard(item, {
          showSave: true,
          showPrepare: true,
          showSelect: false,
          showRemove: false,
        });
        if (card) list.appendChild(card);
      });
    } catch (err) {
      status.textContent = (t().errorPrefix || "Error") + ": " + err.message;
    }
  });

  refreshSaved();
})();
