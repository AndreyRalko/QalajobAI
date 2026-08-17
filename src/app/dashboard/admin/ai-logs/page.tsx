"use client";

import { Fragment, useCallback, useEffect, useState } from "react";
import { useTranslations } from "@/hooks/useTranslations";
import { getAiActionLogs, type AiActionLog } from "@/lib/admin";

const FEATURE_OPTIONS = [
  { value: "", labelKey: "all" },
  { value: "resume_analysis", labelKey: "resumeAnalysis" },
  { value: "resume_enhancement", labelKey: "resumeEnhancement" },
  { value: "vacancy_matching", labelKey: "vacancyMatching" },
  { value: "cover_letter", labelKey: "coverLetter" },
  { value: "interview_prep", labelKey: "interviewPrep" },
  { value: "skill_gap", labelKey: "skillGap" },
  { value: "career_coach", labelKey: "careerCoach" },
  { value: "job_recommendations", labelKey: "jobRecommendations" },
  { value: "assistant", labelKey: "assistant" },
  { value: "resume_import", labelKey: "resumeImport" },
  { value: "hh_adapt_resume", labelKey: "hhAdapt" },
];

function formatDateTime(value: string | null) {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

function StatusBadge({
  status,
  t,
}: {
  status: AiActionLog["status"];
  t: (key: string) => string;
}) {
  const styles = {
    success: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
    failed: "bg-rose-500/15 text-rose-300 border-rose-500/30",
    demo: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  } as const;

  const labels = {
    success: t("admin.aiLogs.statusSuccess"),
    failed: t("admin.aiLogs.statusFailed"),
    demo: t("admin.aiLogs.statusDemo"),
  } as const;

  return (
    <span
      className={`inline-flex px-3 py-1 rounded-full text-xs font-semibold border ${styles[status]}`}
    >
      {labels[status]}
    </span>
  );
}

function JsonBlock({ title, value }: { title: string; value: unknown }) {
  return (
    <div className="bg-white/5 p-4 rounded-2xl border border-white/5">
      <p className="text-xs text-white/40 mb-2">{title}</p>
      <pre className="text-xs text-white/80 whitespace-pre-wrap break-words max-h-64 overflow-auto">
        {typeof value === "string" ? value : JSON.stringify(value, null, 2)}
      </pre>
    </div>
  );
}

export default function AdminAiLogsPage() {
  const { t } = useTranslations();
  const [logs, setLogs] = useState<AiActionLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [featureFilter, setFeatureFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [studentIdFilter, setStudentIdFilter] = useState("");
  const [loginFilter, setLoginFilter] = useState("");
  const [daysFilter, setDaysFilter] = useState("7");
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const loadLogs = useCallback(async () => {
    try {
      setError("");
      const data = await getAiActionLogs({
        feature: featureFilter || undefined,
        status: statusFilter === "all" ? undefined : statusFilter,
        student_id: studentIdFilter.trim() || undefined,
        login: loginFilter.trim() || undefined,
        days: Number(daysFilter) || 7,
        limit: 100,
      });
      setLogs(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setLoading(false);
    }
  }, [daysFilter, featureFilter, loginFilter, statusFilter, studentIdFilter, t]);

  useEffect(() => {
    void loadLogs();
  }, [loadLogs]);

  if (loading) {
    return (
      <div className="p-10 text-white flex justify-center mt-20">
        <div className="animate-spin w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="p-10 text-white">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-4xl font-black bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
            {t("admin.aiLogs.title")}
          </h1>
          <p className="text-white/50 mt-2">{t("admin.aiLogs.subtitle")}</p>
        </div>
        <button
          type="button"
          onClick={() => {
            setLoading(true);
            void loadLogs().finally(() => setLoading(false));
          }}
          className="px-5 py-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 hover:bg-indigo-500/20 transition"
        >
          {t("common.refresh")}
        </button>
      </div>

      <div className="flex flex-wrap gap-4 mt-8">
        <select
          value={featureFilter}
          onChange={(e) => {
            setLoading(true);
            setFeatureFilter(e.target.value);
          }}
          className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white outline-none focus:border-indigo-500 transition"
        >
          {FEATURE_OPTIONS.map((option) => (
            <option key={option.value || "all"} value={option.value}>
              {option.value
                ? t(`admin.aiLogs.features.${option.labelKey}`)
                : t("admin.aiLogs.filterAllFeatures")}
            </option>
          ))}
        </select>

        <select
          value={statusFilter}
          onChange={(e) => {
            setLoading(true);
            setStatusFilter(e.target.value);
          }}
          className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white outline-none focus:border-indigo-500 transition"
        >
          <option value="all">{t("admin.aiLogs.filterAllStatuses")}</option>
          <option value="success">{t("admin.aiLogs.statusSuccess")}</option>
          <option value="failed">{t("admin.aiLogs.statusFailed")}</option>
          <option value="demo">{t("admin.aiLogs.statusDemo")}</option>
        </select>

        <input
          type="text"
          placeholder={t("admin.aiLogs.studentIdPlaceholder")}
          value={studentIdFilter}
          onChange={(e) => setStudentIdFilter(e.target.value)}
          className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white w-44 outline-none focus:border-indigo-500 transition"
        />

        <input
          type="text"
          placeholder={t("admin.aiLogs.loginPlaceholder")}
          value={loginFilter}
          onChange={(e) => setLoginFilter(e.target.value)}
          className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white w-52 outline-none focus:border-indigo-500 transition"
        />

        <select
          value={daysFilter}
          onChange={(e) => {
            setLoading(true);
            setDaysFilter(e.target.value);
          }}
          className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white outline-none focus:border-indigo-500 transition"
        >
          <option value="1">{t("admin.aiLogs.days1")}</option>
          <option value="7">{t("admin.aiLogs.days7")}</option>
          <option value="30">{t("admin.aiLogs.days30")}</option>
          <option value="90">{t("admin.aiLogs.days90")}</option>
        </select>

        <button
          type="button"
          onClick={() => {
            setLoading(true);
            void loadLogs().finally(() => setLoading(false));
          }}
          className="px-5 py-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition"
        >
          {t("admin.aiLogs.applyFilters")}
        </button>
      </div>

      {error && (
        <div className="mt-6 rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-rose-200">
          {error}
        </div>
      )}

      <div className="mt-8 rounded-3xl overflow-hidden border border-white/10 bg-white/[0.02]">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-white/5 text-white/50 font-medium">
              <tr>
                <th className="p-5">{t("admin.aiLogs.time")}</th>
                <th className="p-5">{t("admin.aiLogs.studentId")}</th>
                <th className="p-5">{t("admin.aiLogs.feature")}</th>
                <th className="p-5">{t("admin.aiLogs.status")}</th>
                <th className="p-5">{t("admin.aiLogs.duration")}</th>
                <th className="p-5">{t("admin.aiLogs.details")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-10 text-center text-white/40">
                    {t("admin.aiLogs.noLogs")}
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <Fragment key={log.id}>
                    <tr className="hover:bg-white/5 transition">
                      <td className="p-5">{formatDateTime(log.created_at)}</td>
                      <td className="p-5 font-medium">{log.student_id || "—"}</td>
                      <td className="p-5">
                        <div>{log.feature_label}</div>
                        <div className="text-xs text-white/40 mt-1">{log.endpoint}</div>
                      </td>
                      <td className="p-5">
                        <StatusBadge status={log.status} t={t} />
                      </td>
                      <td className="p-5">
                        <div>{log.duration_ms} ms</div>
                        <div className="text-xs text-white/40 mt-1">
                          {log.provider || "—"} · {log.model_name || "—"}
                        </div>
                      </td>
                      <td className="p-5">
                        <button
                          type="button"
                          onClick={() =>
                            setExpandedId(expandedId === log.id ? null : log.id)
                          }
                          className="text-indigo-300 hover:text-indigo-200 underline"
                        >
                          {t("common.view")}
                        </button>
                      </td>
                    </tr>
                    {expandedId === log.id && (
                      <tr className="bg-indigo-500/5">
                        <td colSpan={6} className="p-5 space-y-4">
                          <JsonBlock
                            title={t("admin.aiLogs.requestPayload")}
                            value={log.request_payload}
                          />
                          <JsonBlock
                            title={t("admin.aiLogs.aiInput")}
                            value={log.ai_input}
                          />
                          <JsonBlock
                            title={t("admin.aiLogs.aiOutput")}
                            value={log.ai_output || "—"}
                          />
                          {log.error_message ? (
                            <JsonBlock
                              title={t("admin.aiLogs.error")}
                              value={log.error_message}
                            />
                          ) : null}
                        </td>
                      </tr>
                    )}
                  </Fragment>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
