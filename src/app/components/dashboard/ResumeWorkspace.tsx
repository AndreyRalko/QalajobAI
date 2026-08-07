"use client";

import jsPDF from "jspdf";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { useVacancyContext } from "@/app/dashboard/student/ai/vacancy-context";
import {
  aiGenerateCoverLetter,
  aiImportResumePdf,
  aiImportResumeText,
  aiInterviewPrep,
  aiResumeAssistant,
  aiResumeEnhance,
  getMyResume,
  getResumeAssistantChat,
  hhAdaptResume,
  saveMyResume,
  type AiChatMessage,
  type WorkspaceMode,
} from "@/lib/api";
import { useTranslations } from "@/hooks/useTranslations";
import { getAccessToken } from "@/lib/session";
import { workspaceHref } from "@/lib/workspace-routes";

type MobileTab = "chat" | "draft";
type SaveStatus = "idle" | "dirty" | "saving" | "saved" | "error";

type ModeState = {
  messages: AiChatMessage[];
  chatId: number | null;
  draft: string;
};

type Props = {
  mode: WorkspaceMode;
};

const emptyMode = (): ModeState => ({
  messages: [],
  chatId: null,
  draft: "",
});

export default function ResumeWorkspace({ mode }: Props) {
  const router = useRouter();
  const {
    jobTitle,
    setJobTitle,
    company,
    setCompany,
    jobDescription,
    setJobDescription,
  } = useVacancyContext();
  const { t, locale } = useTranslations();
  const chatEndRef = useRef<HTMLDivElement>(null);
  const autosaveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const skipAutosave = useRef(true);
  const aiBusy = useRef(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [authed, setAuthed] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [mobileTab, setMobileTab] = useState<MobileTab>("chat");

  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [enhancing, setEnhancing] = useState(false);
  const [adapting, setAdapting] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [importing, setImporting] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [importText, setImportText] = useState("");
  const [saveStatus, setSaveStatus] = useState<SaveStatus>("idle");

  const [modes, setModes] = useState<Record<WorkspaceMode, ModeState>>({
    resume: emptyMode(),
    cover_letter: emptyMode(),
    interview: emptyMode(),
    mock_interview: emptyMode(),
  });

  const [tone, setTone] = useState("professional");
  const [difficulty, setDifficulty] = useState("medium");

  const active = modes[mode];
  const activeDraft = active.draft;

  const getJobContext = () => {
    const title = jobTitle.trim();
    const comp = company.trim();
    const desc = jobDescription.trim();
    if (!title && !comp && !desc) return undefined;
    return {
      jobTitle: title,
      company: comp,
      jobDescription: desc,
    };
  };

  const hasVacancyContext = Boolean(
    jobTitle.trim() || company.trim() || jobDescription.trim()
  );

  const quickActions = useMemo(() => {
    if (mode === "cover_letter") {
      return [
        t("aiPage.coverQuickWrite"),
        t("aiPage.coverQuickShorten"),
        t("aiPage.coverQuickStronger"),
      ];
    }
    if (mode === "mock_interview") {
      return [
        t("aiPage.mockQuickStart"),
        t("aiPage.mockQuickHarder"),
        t("aiPage.mockQuickFinish"),
      ];
    }
    if (mode === "interview") {
      return [
        t("aiPage.interviewQuickPack"),
        t("aiPage.interviewQuickBehavioral"),
        t("aiPage.interviewQuickAnswers"),
      ];
    }
    return [
      t("aiPage.quickStart"),
      t("aiPage.quickImprove"),
      t("aiPage.quickSummary"),
      t("aiPage.quickSkills"),
      t("aiPage.quickExperience"),
      t("aiPage.quickForRole"),
    ];
  }, [mode, t]);

  const updateActive = (patch: Partial<ModeState>) => {
    setModes((prev) => ({
      ...prev,
      [mode]: { ...prev[mode], ...patch },
    }));
  };

  const setActiveDraft = (draft: string) => {
    updateActive({ draft });
  };

  useEffect(() => {
    setQuestion("");
    setMobileTab("chat");
  }, [mode]);

  useEffect(() => {
    skipAutosave.current = true;
    setLoaded(false);

    const load = async () => {
      const token = getAccessToken();
      if (!token) {
        setAuthed(false);
        setLoaded(true);
        return;
      }
      setAuthed(true);

      try {
        const [resume, chat] = await Promise.all([
          getMyResume().catch(() => null),
          getResumeAssistantChat(mode).catch(() => null),
        ]);

        setModes((prev) => ({
          ...prev,
          resume: {
            ...prev.resume,
            draft: resume?.content || prev.resume.draft,
          },
          [mode]: {
            messages: chat?.messages || [],
            chatId: chat?.chat_id ?? null,
            draft:
              mode === "resume"
                ? resume?.content || ""
                : prev[mode]?.draft || "",
          },
        }));
      } catch (error) {
        console.error(error);
      } finally {
        setLoaded(true);
        setTimeout(() => {
          skipAutosave.current = false;
        }, 100);
      }
    };
    void load();
  }, [mode]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [active.messages, loading, mode]);

  // Autosave only resume mode drafts to /resumes/me/
  useEffect(() => {
    if (mode !== "resume") return;
    if (skipAutosave.current || !authed || aiBusy.current) return;
    if (!activeDraft.trim()) return;

    setSaveStatus("dirty");
    if (autosaveTimer.current) clearTimeout(autosaveTimer.current);

    autosaveTimer.current = setTimeout(() => {
      void (async () => {
        setSaveStatus("saving");
        try {
          await saveMyResume(activeDraft);
          setSaveStatus("saved");
        } catch (error) {
          console.error(error);
          setSaveStatus("error");
        }
      })();
    }, 800);

    return () => {
      if (autosaveTimer.current) clearTimeout(autosaveTimer.current);
    };
  }, [activeDraft, authed, mode]);

  const persistResume = async (content: string) => {
    if (!content.trim()) return;
    setSaveStatus("saving");
    try {
      await saveMyResume(content);
      setSaveStatus("saved");
    } catch (error) {
      console.error(error);
      setSaveStatus("error");
    }
  };

  const sendMessage = async (
    text: string,
    modeOverride?: WorkspaceMode
  ) => {
    const trimmed = text.trim();
    const activeMode = modeOverride || mode;
    if (!trimmed || loading || !authed) return;

    const current = modes[activeMode];
    const history = current.messages;
    const chatId = current.chatId;
    const draft = current.draft;

    setModes((prev) => ({
      ...prev,
      [activeMode]: {
        ...prev[activeMode],
        messages: [...history, { role: "user", content: trimmed }],
      },
    }));
    setQuestion("");
    setLoading(true);
    aiBusy.current = true;

    try {
      const data = await aiResumeAssistant(
        trimmed,
        history,
        locale,
        draft,
        chatId,
        activeMode,
        activeMode === "resume" ? undefined : modes.resume.draft,
        getJobContext()
      );

      const nextDraft =
        data.document_draft ??
        (activeMode === "resume" ? data.resume_draft : null) ??
        null;

      setModes((prev) => ({
        ...prev,
        [activeMode]: {
          chatId: data.chat_id || prev[activeMode].chatId,
          messages: data.messages?.length
            ? data.messages
            : [
                ...prev[activeMode].messages,
                {
                  role: "assistant" as const,
                  content: data.reply || t("aiPage.noResponse"),
                },
              ],
          draft: nextDraft ?? prev[activeMode].draft,
        },
      }));

      if (activeMode === "resume" && nextDraft) {
        skipAutosave.current = true;
        await persistResume(nextDraft);
        skipAutosave.current = false;
      }
    } catch (error) {
      console.error(error);
      setModes((prev) => ({
        ...prev,
        [activeMode]: {
          ...prev[activeMode],
          messages: [
            ...prev[activeMode].messages,
            { role: "assistant", content: t("aiPage.aiError") },
          ],
        },
      }));
    } finally {
      setLoading(false);
      aiBusy.current = false;
    }
  };

  const handleEnhance = async () => {
    if (mode !== "resume" || !activeDraft.trim() || enhancing || !authed) return;
    setEnhancing(true);
    aiBusy.current = true;
    try {
      const data = await aiResumeEnhance(activeDraft, locale);
      if (data.enhancedResume) {
        skipAutosave.current = true;
        setActiveDraft(data.enhancedResume);
        await persistResume(data.enhancedResume);
        skipAutosave.current = false;
      }
    } catch (error) {
      console.error(error);
      setSaveStatus("error");
    } finally {
      setEnhancing(false);
      aiBusy.current = false;
    }
  };

  const handleAdaptToVacancy = async () => {
    if (!authed || adapting) return;
    const text = jobDescription.trim();
    const title = jobTitle.trim();
    if (!text && !title) return;

    setAdapting(true);
    aiBusy.current = true;
    try {
      const data = await hhAdaptResume({
        vacancyText: text || title,
        vacancyTitle: title,
        resume: modes.resume.draft,
        language: locale,
        save: true,
      });
      const adapted = data.adapted_resume || data.document_draft || "";
      skipAutosave.current = true;
      setModes((prev) => ({
        ...prev,
        resume: { ...prev.resume, draft: adapted },
      }));
      await persistResume(adapted);
      skipAutosave.current = false;
      router.push(workspaceHref("resume"));
      setMobileTab("draft");
    } catch (error) {
      console.error(error);
      setSaveStatus("error");
    } finally {
      setAdapting(false);
      aiBusy.current = false;
    }
  };

  const handleGenerate = async () => {
    if (!authed || generating) return;
    if (!jobTitle.trim()) return;

    setGenerating(true);
    aiBusy.current = true;
    try {
      if (mode === "cover_letter") {
        const data = await aiGenerateCoverLetter({
          jobTitle: jobTitle.trim(),
          company: company.trim(),
          jobDescription: jobDescription.trim(),
          tone,
          resume: modes.resume.draft,
          language: locale,
        });
        const letter = data.document_draft || data.cover_letter;
        setModes((prev) => ({
          ...prev,
          cover_letter: {
            ...prev.cover_letter,
            draft: letter,
            messages: [
              ...prev.cover_letter.messages,
              { role: "assistant", content: t("aiPage.coverGenerated") },
            ],
          },
        }));
      } else if (mode === "interview") {
        const data = await aiInterviewPrep({
          jobTitle: jobTitle.trim(),
          company: company.trim(),
          requirements: jobDescription.trim(),
          difficulty,
          language: locale,
        });
        setModes((prev) => ({
          ...prev,
          interview: {
            ...prev.interview,
            draft: data.document_draft || "",
            messages: [
              ...prev.interview.messages,
              { role: "assistant", content: t("aiPage.interviewGenerated") },
            ],
          },
        }));
      }
    } catch (error) {
      console.error(error);
      setModes((prev) => ({
        ...prev,
        [mode]: {
          ...prev[mode],
          messages: [
            ...prev[mode].messages,
            { role: "assistant", content: t("aiPage.aiError") },
          ],
        },
      }));
    } finally {
      setGenerating(false);
      aiBusy.current = false;
    }
  };

  const handleDownloadPDF = () => {
    if (!activeDraft.trim()) return;
    const pdf = new jsPDF();
    const lines = pdf.splitTextToSize(activeDraft, 180);
    pdf.setFontSize(12);
    pdf.text(lines, 15, 20);
    const name =
      mode === "cover_letter"
        ? "cover-letter.pdf"
        : mode === "interview"
          ? "interview-prep.pdf"
          : mode === "mock_interview"
            ? "mock-interview-scorecard.pdf"
            : "resume.pdf";
    pdf.save(name);
  };

  const handleNewChat = () => {
    updateActive({
      chatId: null,
      messages: [],
      draft: mode === "resume" ? active.draft : "",
    });
    setQuestion("");
  };

  const startMockInterview = async () => {
    const role = jobTitle.trim();
    if (!role) {
      alert(t("aiPage.mockNeedRole"));
      return;
    }
    const companyPart = company.trim()
      ? ` ${t("aiPage.mockAtCompany")} ${company.trim()}`
      : "";
    const desc = jobDescription.trim()
      ? `\n${t("aiPage.jobDescription")}: ${jobDescription.trim()}`
      : "";
    const starter = `${t("aiPage.mockStartMessage")} ${role}${companyPart}.${desc}`;

    setMobileTab("chat");
    setQuestion("");
    setLoading(true);
    aiBusy.current = true;

    // Clear local session immediately so UI doesn't show old waiter/other role chat
    setModes((prev) => ({
      ...prev,
      mock_interview: { chatId: null, messages: [], draft: "" },
    }));

    try {
      const data = await aiResumeAssistant(
        starter,
        [],
        locale,
        "",
        null,
        "mock_interview",
        modes.resume.draft,
        {
          jobTitle: role,
          company: company.trim(),
          jobDescription: jobDescription.trim(),
          newSession: true,
        }
      );
      setModes((prev) => ({
        ...prev,
        mock_interview: {
          chatId: data.chat_id || null,
          messages: data.messages?.length
            ? data.messages
            : [
                { role: "user", content: starter },
                {
                  role: "assistant",
                  content: data.reply || t("aiPage.noResponse"),
                },
              ],
          draft: data.document_draft || "",
        },
      }));
    } catch (error) {
      console.error(error);
      setModes((prev) => ({
        ...prev,
        mock_interview: {
          chatId: null,
          draft: "",
          messages: [{ role: "assistant", content: t("aiPage.aiError") }],
        },
      }));
    } finally {
      setLoading(false);
      aiBusy.current = false;
    }
  };

  const finishMockInterview = async () => {
    if (loading) return;
    await sendMessage(t("aiPage.mockFinishMessage"), "mock_interview");
  };

  const handleManualSave = async () => {
    if (mode !== "resume" || !activeDraft.trim() || !authed) return;
    await persistResume(activeDraft);
  };

  const handleImportText = async (source: "paste" | "linkedin") => {
    if (!importText.trim() || importing) return;
    setImporting(true);
    try {
      const data = await aiImportResumeText({
        text: importText,
        source,
        language: locale,
        save: true,
      });
      const resume = data.resume || data.document_draft;
      skipAutosave.current = true;
      setModes((prev) => ({
        ...prev,
        resume: { ...prev.resume, draft: resume },
      }));
      await persistResume(resume);
      skipAutosave.current = false;
      router.push(workspaceHref("resume"));
      setShowImport(false);
      setImportText("");
      setMobileTab("draft");
    } catch (error) {
      console.error(error);
      setSaveStatus("error");
    } finally {
      setImporting(false);
    }
  };

  const handleImportPdf = async (file: File) => {
    setImporting(true);
    try {
      const data = await aiImportResumePdf(file, locale, true);
      const resume = data.resume || data.document_draft;
      skipAutosave.current = true;
      setModes((prev) => ({
        ...prev,
        resume: { ...prev.resume, draft: resume },
      }));
      await persistResume(resume);
      skipAutosave.current = false;
      router.push(workspaceHref("resume"));
      setShowImport(false);
      setMobileTab("draft");
    } catch (error) {
      console.error(error);
      setSaveStatus("error");
    } finally {
      setImporting(false);
    }
  };

  const saveLabel =
    mode !== "resume"
      ? ""
      : saveStatus === "saving"
        ? t("aiPage.saveStatusSaving")
        : saveStatus === "saved"
          ? t("aiPage.saveStatusSaved")
          : saveStatus === "error"
            ? t("aiPage.saveStatusError")
            : saveStatus === "dirty"
              ? t("aiPage.saveStatusDirty")
              : t("aiPage.saveStatusIdle");

  const draftTitle =
    mode === "cover_letter"
      ? t("aiPage.coverDraftTitle")
      : mode === "interview"
        ? t("aiPage.interviewDraftTitle")
        : mode === "mock_interview"
          ? t("aiPage.mockDraftTitle")
          : t("aiPage.draftTitle");

  const draftPlaceholder =
    mode === "cover_letter"
      ? t("aiPage.coverDraftPlaceholder")
      : mode === "interview"
        ? t("aiPage.interviewDraftPlaceholder")
        : mode === "mock_interview"
          ? t("aiPage.mockDraftPlaceholder")
          : t("aiPage.draftPlaceholder");

  const chatTitle =
    mode === "cover_letter"
      ? t("aiPage.coverChatTitle")
      : mode === "interview"
        ? t("aiPage.interviewChatTitle")
        : mode === "mock_interview"
          ? t("aiPage.mockChatTitle")
          : t("aiPage.chatTitle");

  if (!loaded) {
    return (
      <div className="p-6 md:p-10">
        <p className="text-white/40">{t("aiPage.thinking")}</p>
      </div>
    );
  }

  if (!authed) {
    return (
      <div className="p-6 md:p-10">
        <div className="max-w-xl rounded-3xl border border-white/10 bg-white/5 p-8">
          <h1 className="text-3xl font-black">{t("aiPage.title")}</h1>
          <p className="text-white/50 mt-3">{t("aiPage.loginRequired")}</p>
          <Link
            href="/login"
            className="inline-flex mt-6 px-6 py-3 rounded-2xl bg-cyan-500 text-black font-bold"
          >
            {t("navbar.login")}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full min-h-0 p-4 md:p-6 lg:p-8">
      <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4 shrink-0">
        <div>
          <h1 className="text-3xl md:text-4xl font-black">{t("aiPage.title")}</h1>
          <p className="text-white/50 mt-2 max-w-2xl text-sm md:text-base">
            {t("aiPage.description")}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {saveLabel ? (
            <span className="text-xs text-white/40 px-3 py-2">{saveLabel}</span>
          ) : null}
          <button
            type="button"
            onClick={() => setShowImport(true)}
            className="px-4 py-2 rounded-full border border-white/10 bg-white/5 text-sm text-white/70 hover:text-white"
          >
            {t("aiPage.import")}
          </button>
          <button
            type="button"
            onClick={handleNewChat}
            className="px-4 py-2 rounded-full border border-white/10 bg-white/5 text-sm text-white/70 hover:text-white"
          >
            {t("aiPage.newChat")}
          </button>
          {mode === "resume" ? (
            <button
              type="button"
              onClick={() => void handleEnhance()}
              disabled={enhancing || !activeDraft.trim()}
              className="px-4 py-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-sm text-cyan-300 disabled:opacity-50"
            >
              {enhancing ? t("aiPage.enhancing") : t("aiPage.enhance")}
            </button>
          ) : null}
          <button
            type="button"
            onClick={handleDownloadPDF}
            disabled={!activeDraft.trim()}
            className="px-4 py-2 rounded-full border border-white/10 bg-white/5 text-sm text-white/70 disabled:opacity-50"
          >
            {t("aiPage.exportPdf")}
          </button>
          {mode === "resume" ? (
            <button
              type="button"
              onClick={() => void handleManualSave()}
              disabled={saveStatus === "saving" || !activeDraft.trim()}
              className="px-4 py-2 rounded-full bg-cyan-500 text-black text-sm font-bold disabled:opacity-50"
            >
              {t("aiPage.saveDraft")}
            </button>
          ) : null}
        </div>
      </div>

      {/* Vacancy context — shared across all modes */}
      <div className="mt-4 rounded-3xl border border-white/10 bg-white/[0.03] p-4 md:p-5 shrink-0">
        <h2 className="text-sm font-bold text-cyan-300">{t("aiPage.vacancyContextTitle")}</h2>
        <p className="text-white/45 text-xs mt-1 mb-3">{t("aiPage.vacancyContextHint")}</p>

        <div className="grid md:grid-cols-2 gap-3">
          <input
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
            placeholder={t("aiPage.jobTitle")}
            className="px-4 py-2 rounded-2xl bg-white/5 border border-white/10 text-sm outline-none"
          />
          <input
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            placeholder={t("aiPage.company")}
            className="px-4 py-2 rounded-2xl bg-white/5 border border-white/10 text-sm outline-none"
          />
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder={t("aiPage.vacancyPastePlaceholder")}
            rows={5}
            className="md:col-span-2 px-4 py-3 rounded-2xl bg-white/5 border border-white/10 text-sm outline-none resize-none leading-relaxed"
          />
        </div>

        <div className="mt-3 flex flex-wrap items-center gap-2">
          {mode === "resume" ? (
            <button
              type="button"
              onClick={() => void handleAdaptToVacancy()}
              disabled={adapting || !hasVacancyContext}
              className="px-4 py-2 rounded-2xl bg-cyan-500 text-black text-sm font-bold disabled:opacity-50"
            >
              {adapting ? t("aiPage.hhAdapting") : t("aiPage.hhAdapt")}
            </button>
          ) : mode === "mock_interview" ? (
            <>
              <button
                type="button"
                onClick={() => void startMockInterview()}
                disabled={loading || !jobTitle.trim()}
                className="px-4 py-2 rounded-2xl bg-cyan-500 text-black text-sm font-bold disabled:opacity-50"
              >
                {loading ? t("aiPage.thinking") : t("aiPage.mockStart")}
              </button>
              <button
                type="button"
                onClick={() => void finishMockInterview()}
                disabled={loading || active.messages.length === 0}
                className="px-4 py-2 rounded-full border border-white/10 bg-white/5 text-sm text-white/70 disabled:opacity-50"
              >
                {t("aiPage.mockFinish")}
              </button>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="px-4 py-2 rounded-2xl bg-white/5 border border-white/10 text-sm outline-none"
              >
                <option value="easy">{t("aiPage.difficultyEasy")}</option>
                <option value="medium">{t("aiPage.difficultyMedium")}</option>
                <option value="hard">{t("aiPage.difficultyHard")}</option>
              </select>
              <p className="text-xs text-white/40">{t("aiPage.mockHint")}</p>
            </>
          ) : (
            <>
              <button
                type="button"
                onClick={() => void handleGenerate()}
                disabled={generating || !jobTitle.trim()}
                className="px-4 py-2 rounded-2xl bg-cyan-500 text-black text-sm font-bold disabled:opacity-50"
              >
                {generating ? t("aiPage.generating") : t("aiPage.generate")}
              </button>
              {mode === "cover_letter" ? (
                <select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  className="px-4 py-2 rounded-2xl bg-white/5 border border-white/10 text-sm outline-none"
                >
                  <option value="professional">{t("aiPage.toneProfessional")}</option>
                  <option value="friendly">{t("aiPage.toneFriendly")}</option>
                  <option value="creative">{t("aiPage.toneCreative")}</option>
                </select>
              ) : (
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="px-4 py-2 rounded-2xl bg-white/5 border border-white/10 text-sm outline-none"
                >
                  <option value="easy">{t("aiPage.difficultyEasy")}</option>
                  <option value="medium">{t("aiPage.difficultyMedium")}</option>
                  <option value="hard">{t("aiPage.difficultyHard")}</option>
                </select>
              )}
            </>
          )}
        </div>
      </div>

      {/* Mobile tabs */}
      <div className="mt-4 flex gap-2 lg:hidden shrink-0">
        <button
          type="button"
          onClick={() => setMobileTab("chat")}
          className={`flex-1 py-2 rounded-full text-sm font-medium ${
            mobileTab === "chat"
              ? "bg-cyan-500 text-black"
              : "bg-white/5 text-white/60"
          }`}
        >
          {t("aiPage.tabChat")}
        </button>
        <button
          type="button"
          onClick={() => setMobileTab("draft")}
          className={`flex-1 py-2 rounded-full text-sm font-medium ${
            mobileTab === "draft"
              ? "bg-cyan-500 text-black"
              : "bg-white/5 text-white/60"
          }`}
        >
          {t("aiPage.tabResume")}
        </button>
      </div>

      <div className="mt-4 flex flex-wrap gap-2 shrink-0">
        {quickActions.map((action) => (
          <button
            key={action}
            type="button"
            disabled={loading}
            onClick={() => void sendMessage(action)}
            className="px-3 py-1.5 rounded-full border border-white/10 bg-white/5 text-xs md:text-sm text-white/80 hover:border-cyan-500/40 hover:text-cyan-300 disabled:opacity-50"
          >
            {action}
          </button>
        ))}
      </div>

      <div className="mt-4 grid lg:grid-cols-2 gap-4 flex-1 min-h-0">
        <section
          className={`rounded-3xl border border-white/10 bg-white/[0.03] p-4 md:p-5 flex flex-col min-h-[420px] lg:min-h-0 ${
            mobileTab === "chat" ? "flex" : "hidden lg:flex"
          }`}
        >
          <h2 className="text-lg font-bold text-cyan-300 mb-3 shrink-0">
            {chatTitle}
          </h2>

          <div className="flex-1 overflow-y-auto space-y-3 pr-1 min-h-0">
            {active.messages.length === 0 ? (
              <p className="text-white/40">
                {mode === "cover_letter"
                  ? t("aiPage.coverStart")
                  : mode === "interview"
                    ? t("aiPage.interviewStart")
                    : mode === "mock_interview"
                      ? t("aiPage.mockStartHint")
                      : t("aiPage.startConversation")}
              </p>
            ) : (
              active.messages.map((msg, index) => (
                <div
                  key={`${msg.role}-${index}`}
                  className={`p-4 rounded-2xl whitespace-pre-wrap text-sm ${
                    msg.role === "user"
                      ? "bg-cyan-500/10 text-cyan-200 ml-6"
                      : mode === "mock_interview"
                        ? "bg-violet-500/10 border border-violet-500/20 mr-6"
                        : "bg-white/5 mr-6"
                  }`}
                >
                  {mode === "mock_interview" && msg.role === "assistant" ? (
                    <p className="text-[10px] uppercase tracking-wide text-violet-300/80 mb-2">
                      {t("aiPage.mockInterviewer")}
                    </p>
                  ) : null}
                  {msg.content}
                </div>
              ))
            )}
            {loading && (
              <div className="bg-white/5 p-4 rounded-2xl mr-6 text-white/50 text-sm">
                {mode === "mock_interview"
                  ? t("aiPage.mockThinking")
                  : t("aiPage.thinking")}
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="flex gap-3 mt-3 shrink-0">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder={
                mode === "cover_letter"
                  ? t("aiPage.coverPlaceholder")
                  : mode === "interview"
                    ? t("aiPage.interviewPlaceholder")
                    : mode === "mock_interview"
                      ? t("aiPage.mockPlaceholder")
                      : t("aiPage.placeholder")
              }
              rows={2}
              className="flex-1 p-3 rounded-2xl bg-white/5 border border-white/10 outline-none resize-none text-sm"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  void sendMessage(question);
                }
              }}
            />
            <button
              type="button"
              onClick={() => void sendMessage(question)}
              disabled={loading || !question.trim()}
              className="px-5 rounded-2xl bg-cyan-500 text-black font-bold disabled:opacity-50"
            >
              {t("aiPage.send")}
            </button>
          </div>
        </section>

        <section
          className={`rounded-3xl border border-white/10 bg-white/[0.03] p-4 md:p-5 flex flex-col min-h-[420px] lg:min-h-0 ${
            mobileTab === "draft" ? "flex" : "hidden lg:flex"
          }`}
        >
          <div className="flex items-center justify-between gap-3 mb-3 shrink-0">
            <h2 className="text-lg font-bold text-cyan-300">{draftTitle}</h2>
            <span className="text-xs text-white/40">
              {activeDraft.trim().length} {t("aiPage.chars")}
            </span>
          </div>

          <textarea
            value={activeDraft}
            onChange={(e) => setActiveDraft(e.target.value)}
            placeholder={draftPlaceholder}
            className="flex-1 w-full p-4 rounded-2xl bg-[#020617] border border-white/10 outline-none resize-none font-mono text-sm leading-relaxed min-h-0"
          />
        </section>
      </div>

      {/* Import modal */}
      {showImport ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70">
          <div className="w-full max-w-lg rounded-3xl border border-white/10 bg-[#0b1220] p-6">
            <h3 className="text-xl font-bold">{t("aiPage.importTitle")}</h3>
            <p className="text-white/50 text-sm mt-2">
              {t("aiPage.importDescription")}
            </p>

            <div className="mt-4 flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={importing}
                className="px-4 py-2 rounded-full bg-cyan-500 text-black text-sm font-bold disabled:opacity-50"
              >
                {importing ? t("aiPage.importing") : t("aiPage.importPdf")}
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf,.pdf"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) void handleImportPdf(file);
                  e.target.value = "";
                }}
              />
            </div>

            <textarea
              value={importText}
              onChange={(e) => setImportText(e.target.value)}
              placeholder={t("aiPage.importPastePlaceholder")}
              rows={8}
              className="mt-4 w-full p-4 rounded-2xl bg-white/5 border border-white/10 outline-none resize-none text-sm"
            />

            <div className="mt-4 flex flex-wrap gap-2 justify-end">
              <button
                type="button"
                onClick={() => setShowImport(false)}
                className="px-4 py-2 rounded-full border border-white/10 text-sm text-white/70"
              >
                {t("aiPage.importCancel")}
              </button>
              <button
                type="button"
                disabled={importing || !importText.trim()}
                onClick={() => void handleImportText("linkedin")}
                className="px-4 py-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-sm text-cyan-300 disabled:opacity-50"
              >
                {t("aiPage.importLinkedIn")}
              </button>
              <button
                type="button"
                disabled={importing || !importText.trim()}
                onClick={() => void handleImportText("paste")}
                className="px-4 py-2 rounded-full bg-cyan-500 text-black text-sm font-bold disabled:opacity-50"
              >
                {t("aiPage.importPaste")}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
