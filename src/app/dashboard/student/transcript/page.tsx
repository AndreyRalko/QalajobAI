"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "@/hooks/useTranslations";
import {
  getTranscriptsApi,
  getTranscriptSummaryApi,
  type ApiTranscript,
  type ApiTranscriptSummary,
} from "@/lib/api";

export default function StudentTranscriptPage() {
  const { t, lang } = useTranslations();
  const [rows, setRows] = useState<ApiTranscript[]>([]);
  const [summary, setSummary] = useState<ApiTranscriptSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [transcriptRows, transcriptSummary] = await Promise.all([
          getTranscriptsApi(),
          getTranscriptSummaryApi(),
        ]);
        if (cancelled) return;
        setRows(transcriptRows.filter((row) => Number(row.deleted ?? 0) === 0));
        setSummary(transcriptSummary);
      } catch (err) {
        if (cancelled) return;
        console.error(err);
        setError(t("studentTranscript.loadError"));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [t]);

  const subjectName = (row: ApiTranscript) => {
    if (lang === "kz" && row.subject_name_kz) return row.subject_name_kz;
    if (lang === "en" && row.subject_name_en) return row.subject_name_en;
    return row.subject_name_ru || row.subject_name_en || row.subject_name_kz;
  };

  const formatGpa = (gpa: ApiTranscriptSummary["gpa"]) => {
    if (gpa === null || gpa === undefined) return "—";
    const value = typeof gpa === "number" ? gpa : Number(gpa);
    return Number.isFinite(value) ? value.toFixed(2) : "—";
  };

  const formatTotalMark = (totalMark: string | null | undefined) => {
    if (totalMark === null || totalMark === undefined || totalMark === "") {
      return "—";
    }
    const value = Number(totalMark);
    return Number.isFinite(value) ? String(Math.round(value * 100) / 100) : totalMark;
  };

  return (
    <div className="p-6 md:p-10">
      <h1 className="text-5xl font-black">{t("studentTranscript.title")}</h1>
      <p className="text-white/50 mt-2">{t("studentTranscript.subtitle")}</p>

      {loading ? (
        <p className="mt-10 text-white/50">{t("studentTranscript.loading")}</p>
      ) : error ? (
        <p className="mt-10 text-red-400">{error}</p>
      ) : (
        <>
          {summary && (
            <div className="mt-10 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
                <p className="text-white/50 text-sm">
                  {t("studentTranscript.studentId")}
                </p>
                <p className="text-2xl font-bold mt-1">
                  {summary.student_id || "—"}
                </p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
                <p className="text-white/50 text-sm">
                  {t("studentTranscript.subjects")}
                </p>
                <p className="text-2xl font-bold mt-1">{summary.subjects}</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
                <p className="text-white/50 text-sm">
                  {t("studentTranscript.credits")}
                </p>
                <p className="text-2xl font-bold mt-1">
                  {summary.credits ?? "—"}
                </p>
              </div>
              <div className="rounded-2xl border border-cyan-500/20 bg-cyan-500/10 p-5">
                <p className="text-cyan-400/70 text-sm">
                  {t("studentTranscript.gpa")}
                </p>
                <p className="text-2xl font-bold text-cyan-400 mt-1">
                  {formatGpa(summary.gpa)}
                </p>
              </div>
            </div>
          )}

          {rows.length === 0 ? (
            <p className="mt-10 text-white/50">{t("studentTranscript.noData")}</p>
          ) : (
            <div className="mt-10 overflow-x-auto rounded-3xl border border-white/10">
              <table className="w-full min-w-[820px] text-left text-sm">
                <thead className="bg-white/5 text-white/50 uppercase text-xs tracking-wider">
                  <tr>
                    <th className="px-4 py-3">{t("studentTranscript.code")}</th>
                    <th className="px-4 py-3">
                      {t("studentTranscript.subject")}
                    </th>
                    <th className="px-4 py-3">
                      {t("studentTranscript.course")}
                    </th>
                    <th className="px-4 py-3">
                      {t("studentTranscript.term")}
                    </th>
                    <th className="px-4 py-3">
                      {t("studentTranscript.credits")}
                    </th>
                    <th className="px-4 py-3">
                      {t("studentTranscript.grade")}
                    </th>
                    <th className="px-4 py-3">
                      {t("studentTranscript.totalMark")}
                    </th>
                    <th className="px-4 py-3">
                      {t("studentTranscript.passed")}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <tr
                      key={row.id}
                      className="border-t border-white/5 hover:bg-white/[0.02]"
                    >
                      <td className="px-4 py-3 font-mono text-cyan-400">
                        {row.subject_code}
                      </td>
                      <td className="px-4 py-3">{subjectName(row)}</td>
                      <td className="px-4 py-3">{row.course_number ?? "—"}</td>
                      <td className="px-4 py-3">{row.term ?? "—"}</td>
                      <td className="px-4 py-3">{row.credits || "—"}</td>
                      <td className="px-4 py-3">
                        {row.alpha_mark || row.numeral_mark || "—"}
                      </td>
                      <td className="px-4 py-3 font-semibold">
                        {formatTotalMark(row.total_mark)}
                      </td>
                      <td className="px-4 py-3">
                        {row.is_passed ? "✓" : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
