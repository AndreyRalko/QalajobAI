(function () {
  const root = document.getElementById("workspace");
  if (!root || !window.QJ || !window.QJ.api) return;

  const mode = root.dataset.mode || "resume";
  const chatEl = document.getElementById("chatMessages");
  const draftEl = document.getElementById("draft");
  const questionEl = document.getElementById("question");
  const statusEl = document.getElementById("saveStatus");
  const jobTitleEl = document.getElementById("jobTitle");
  const companyEl = document.getElementById("company");
  const jobDescEl = document.getElementById("jobDescription");
  const savedSelect = document.getElementById("savedVacancySelect");
  const savedEmpty = document.getElementById("savedVacancyEmpty");
  let chatId = null;
  let busy = false;
  let savedItems = [];
  const t = () => window.QJ.i18n || {};

  function jobContextFields() {
    return {
      job_title: jobTitleEl.value.trim(),
      company: companyEl.value.trim(),
      job_description: jobDescEl.value.trim(),
    };
  }

  function hasVacancy() {
    const ctx = jobContextFields();
    return !!(ctx.job_title || ctx.company || ctx.job_description);
  }

  function applyContext(ctx) {
    if (!ctx) return;
    jobTitleEl.value = ctx.jobTitle || ctx.title || "";
    companyEl.value = ctx.company || "";
    jobDescEl.value = ctx.jobDescription || ctx.description || "";
  }

  function syncSelectValue(selectedId) {
    if (!savedSelect) return;
    const id = selectedId != null ? String(selectedId) : "";
    if (id && Array.from(savedSelect.options).some((o) => o.value === id)) {
      savedSelect.value = id;
    } else {
      savedSelect.value = "";
    }
  }

  function fillSavedSelect(items, selectedId) {
    if (!savedSelect) return;
    savedItems = items || [];
    const placeholder =
      t().pickSavedPlaceholder || "— choose from saved —";
    savedSelect.innerHTML = "";
    const emptyOpt = document.createElement("option");
    emptyOpt.value = "";
    emptyOpt.textContent = placeholder;
    savedSelect.appendChild(emptyOpt);

    savedItems.forEach((item) => {
      const opt = document.createElement("option");
      opt.value = String(item.id);
      const label = [item.title, item.company].filter(Boolean).join(" · ");
      opt.textContent = (item.is_selected ? "★ " : "") + label;
      savedSelect.appendChild(opt);
    });

    if (savedEmpty) {
      savedEmpty.hidden = savedItems.length > 0;
    }
    syncSelectValue(
      selectedId ||
        (savedItems.find((x) => x.is_selected) || {}).id ||
        ""
    );
  }

  async function loadSavedVacancies() {
    if (!window.QJ.vacancy) return [];
    try {
      const items = await window.QJ.vacancy.list();
      return items;
    } catch (_) {
      return [];
    }
  }

  async function onSavedSelectChange() {
    const id = savedSelect && savedSelect.value;
    if (!id) return;
    try {
      const updated = await window.QJ.vacancy.select(id);
      const ctx = window.QJ.vacancy.toContext(updated);
      window.QJ.vacancy.saveLocal(ctx);
      applyContext(ctx);
      // refresh stars in dropdown
      const items = await loadSavedVacancies();
      fillSavedSelect(items, updated.id);
    } catch (err) {
      alert((t().errorPrefix || "Error") + ": " + err.message);
    }
  }

  function persistFieldsLocally() {
    if (!window.QJ.vacancy) return;
    const ctx = {
      jobTitle: jobTitleEl.value.trim(),
      company: companyEl.value.trim(),
      jobDescription: jobDescEl.value.trim(),
    };
    if (ctx.jobTitle) window.QJ.vacancy.saveLocal(ctx);
  }

  function addMsg(role, content) {
    const div = document.createElement("div");
    div.className = "msg " + role;
    div.textContent = content;
    chatEl.appendChild(div);
    chatEl.scrollTop = chatEl.scrollHeight;
  }

  async function loadVacancyContext() {
    const items = await loadSavedVacancies();
    let selected = items.find((x) => x.is_selected) || null;
    let ctx = null;

    if (selected) {
      ctx = window.QJ.vacancy.toContext(selected);
      window.QJ.vacancy.saveLocal(ctx);
    } else {
      ctx = window.QJ.vacancy ? window.QJ.vacancy.loadLocal() : null;
      // If local ctx matches a saved title, try to highlight it
      if (ctx && ctx.hh_id) {
        selected =
          items.find((x) => String(x.hh_id) === String(ctx.hh_id)) || null;
      }
    }

    fillSavedSelect(items, selected && selected.id);
    applyContext(ctx);
  }

  async function loadResume() {
    try {
      const resume = await window.QJ.api("/resumes/me/");
      if (resume && resume.content) draftEl.value = resume.content;
    } catch (_) { /* first visit ok */ }
  }

  async function loadChat() {
    try {
      const data = await window.QJ.api(
        "/ai/career-coach/?mode=" + encodeURIComponent(mode)
      );
      if (data && data.chat_id) chatId = data.chat_id;
      if (data && Array.isArray(data.messages)) {
        chatEl.innerHTML = "";
        data.messages.forEach((m) =>
          addMsg(m.role || "assistant", m.content || "")
        );
      }
    } catch (_) { /* empty chat */ }
  }

  async function send() {
    const question = questionEl.value.trim();
    if (!question || busy) return;
    busy = true;
    persistFieldsLocally();
    addMsg("user", question);
    questionEl.value = "";
    try {
      const payload = {
        mode,
        message: question,
        chat_id: chatId,
        draft: draftEl.value,
        resume_draft: draftEl.value,
        ...jobContextFields(),
      };
      const data = await window.QJ.api("/ai/career-coach/", {
        method: "POST",
        json: payload,
      });
      if (data.chat_id) chatId = data.chat_id;
      if (data.reply) addMsg("assistant", data.reply);
      const nextDraft = data.document_draft || data.resume_draft;
      if (nextDraft) draftEl.value = nextDraft;
    } catch (err) {
      addMsg(
        "assistant",
        (t().errorPrefix || "Error") + ": " + err.message
      );
    } finally {
      busy = false;
    }
  }

  async function saveDraft() {
    statusEl.textContent = t().saving || "Saving…";
    try {
      await window.QJ.api("/resumes/me/", {
        method: "PUT",
        json: { content: draftEl.value },
      });
      statusEl.textContent = t().saved || "Saved";
    } catch (err) {
      statusEl.textContent = (t().errorPrefix || "Error") + ": " + err.message;
    }
  }

  async function enhance() {
    statusEl.textContent = t().enhancing || "Enhancing…";
    persistFieldsLocally();
    try {
      const data = await window.QJ.api("/ai/resume-enhance/", {
        method: "POST",
        json: { resume: draftEl.value, ...jobContextFields() },
      });
      if (data.enhanced_resume || data.enhancedResume) {
        draftEl.value = data.enhanced_resume || data.enhancedResume;
      }
      statusEl.textContent = t().enhanced || "Enhanced";
    } catch (err) {
      statusEl.textContent = (t().errorPrefix || "Error") + ": " + err.message;
    }
  }

  async function adaptResume() {
    if (!hasVacancy()) {
      alert(t().selectVacancyHint || "Select a vacancy first");
      return;
    }
    persistFieldsLocally();
    statusEl.textContent = t().adaptResume || "Adapting…";
    const ctx = jobContextFields();
    try {
      const data = await window.QJ.api("/ai/hh/adapt-resume/", {
        method: "POST",
        json: {
          resume: draftEl.value,
          vacancy_title: ctx.job_title,
          vacancy_text: [ctx.job_title, ctx.company, ctx.job_description]
            .filter(Boolean)
            .join("\n"),
          vacancy_description: ctx.job_description,
        },
      });
      const adapted =
        data.document_draft ||
        data.adapted_resume ||
        data.adaptedResume ||
        data.resume;
      if (adapted) draftEl.value = adapted;
      addMsg(
        "assistant",
        (t().adaptResume || "Adapt") + ": OK — " + (ctx.job_title || "")
      );
      statusEl.textContent = t().enhanced || "Done";
    } catch (err) {
      statusEl.textContent = (t().errorPrefix || "Error") + ": " + err.message;
    }
  }

  async function genCover() {
    if (!hasVacancy()) {
      alert(t().selectVacancyHint || "Select a vacancy first");
      return;
    }
    persistFieldsLocally();
    statusEl.textContent = t().genCover || "Generating…";
    try {
      const data = await window.QJ.api("/ai/cover-letter/", {
        method: "POST",
        json: {
          ...jobContextFields(),
          resume: draftEl.value,
          tone: "professional",
        },
      });
      const letter =
        data.document_draft || data.cover_letter || data.coverLetter || "";
      if (letter) {
        if (mode === "cover_letter") {
          draftEl.value = letter;
        } else {
          draftEl.value =
            (draftEl.value ? draftEl.value + "\n\n---\n\n" : "") + letter;
        }
      }
      if (data.reply) addMsg("assistant", data.reply);
      else if (letter) addMsg("assistant", letter.slice(0, 500));
      statusEl.textContent = t().saved || "Done";
    } catch (err) {
      statusEl.textContent = (t().errorPrefix || "Error") + ": " + err.message;
    }
  }

  async function genInterview() {
    if (!hasVacancy()) {
      alert(t().selectVacancyHint || "Select a vacancy first");
      return;
    }
    persistFieldsLocally();
    statusEl.textContent = t().genInterview || "Generating…";
    const ctx = jobContextFields();
    try {
      const data = await window.QJ.api("/ai/interview-prep/", {
        method: "POST",
        json: {
          job_title: ctx.job_title,
          company: ctx.company,
          job_description: ctx.job_description,
          requirements: ctx.job_description,
          resume: draftEl.value,
          difficulty: "medium",
        },
      });
      const doc = data.document_draft || data.plan || "";
      if (doc) {
        if (mode === "interview" || mode === "mock_interview") {
          draftEl.value = doc;
        } else {
          draftEl.value =
            (draftEl.value ? draftEl.value + "\n\n---\n\n" : "") + doc;
        }
      }
      if (data.reply) addMsg("assistant", data.reply);
      else if (doc) addMsg("assistant", doc.slice(0, 500));
      statusEl.textContent = t().saved || "Done";
    } catch (err) {
      statusEl.textContent = (t().errorPrefix || "Error") + ": " + err.message;
    }
  }

  function downloadPdf() {
    const text = draftEl.value || "";
    const win = window.open("", "_blank");
    win.document.write(
      "<pre style='font-family:Georgia,serif;white-space:pre-wrap;padding:24px'>" +
        text.replace(/[<>&]/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;" }[c])) +
        "</pre>"
    );
    win.document.close();
    win.focus();
    win.print();
  }

  async function clearVacancy() {
    jobTitleEl.value = "";
    companyEl.value = "";
    jobDescEl.value = "";
    if (savedSelect) savedSelect.value = "";
    if (window.QJ.vacancy) {
      window.QJ.vacancy.clearLocal();
      try {
        await window.QJ.vacancy.clearSelected();
        const items = await loadSavedVacancies();
        fillSavedSelect(items, "");
      } catch (_) { /* ignore */ }
    }
  }

  document.getElementById("sendBtn").addEventListener("click", send);
  questionEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  });
  document.getElementById("saveBtn").addEventListener("click", saveDraft);
  document.getElementById("enhanceBtn").addEventListener("click", enhance);
  document.getElementById("pdfBtn").addEventListener("click", downloadPdf);
  document.getElementById("adaptBtn").addEventListener("click", adaptResume);
  document.getElementById("coverBtn").addEventListener("click", genCover);
  document
    .getElementById("interviewBtn")
    .addEventListener("click", genInterview);
  document
    .getElementById("clearVacancyBtn")
    .addEventListener("click", clearVacancy);
  if (savedSelect) {
    savedSelect.addEventListener("change", onSavedSelectChange);
  }

  ["change", "blur"].forEach((ev) => {
    jobTitleEl.addEventListener(ev, persistFieldsLocally);
    companyEl.addEventListener(ev, persistFieldsLocally);
    jobDescEl.addEventListener(ev, persistFieldsLocally);
  });

  Promise.all([loadVacancyContext(), loadResume(), loadChat()]);
})();
