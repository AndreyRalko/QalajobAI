"use client";

import { Fragment, useCallback, useEffect, useState } from "react";
import { useTranslations } from "@/hooks/useTranslations";
import { getLmsSyncLogs, getLmsSyncSchedule, runLmsSync, saveLmsSyncSchedule, type LmsSyncLog, type LmsSyncSchedule } from "@/lib/admin";

function formatDateTime(value: string | null) {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

function formatDuration(seconds: number | null) {
  if (seconds === null) return "—";
  if (seconds < 60) return `${seconds} с`;
  const minutes = Math.floor(seconds / 60);
  const rest = seconds % 60;
  return `${minutes} мин ${rest} с`;
}

function StatusBadge({
  status,
  t,
}: {
  status: LmsSyncLog["status"];
  t: (key: string) => string;
}) {
  const styles = {
    running: "bg-amber-500/15 text-amber-300 border-amber-500/30",
    success: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
    failed: "bg-rose-500/15 text-rose-300 border-rose-500/30",
  } as const;

  const labels = {
    running: t("admin.lmsSync.statusRunning"),
    success: t("admin.lmsSync.statusSuccess"),
    failed: t("admin.lmsSync.statusFailed"),
  } as const;

  return (
    <span
      className={`inline-flex px-3 py-1 rounded-full text-xs font-semibold border ${styles[status]}`}
    >
      {labels[status]}
    </span>
  );
}

export default function AdminLmsSyncPage() {
  const { t } = useTranslations();
  const [logs, setLogs] = useState<LmsSyncLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("all");
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [syncing, setSyncing] = useState(false);
  const [schedule, setSchedule] = useState<LmsSyncSchedule | null>(null);
  const [scheduleTime, setScheduleTime] = useState("02:00");
  const [scheduleEnabled, setScheduleEnabled] = useState(true);
  const [savingSchedule, setSavingSchedule] = useState(false);
  const [scheduleMessage, setScheduleMessage] = useState("");

  const loadSchedule = useCallback(async () => {
    try {
      const data = await getLmsSyncSchedule();
      setSchedule(data);
      setScheduleTime(data.time);
      setScheduleEnabled(data.enabled);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    }
  }, [t]);

  const loadLogs = useCallback(async () => {
    try {
      setError("");
      const data = await getLmsSyncLogs({
        status: statusFilter === "all" ? undefined : statusFilter,
        limit: 100,
      });
      setLogs(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setLoading(false);
    }
  }, [statusFilter, t]);

  useEffect(() => {
    void loadLogs();
    void loadSchedule();
  }, [loadLogs, loadSchedule]);

  useEffect(() => {
    const hasRunning = logs.some((log) => log.status === "running");
    if (!hasRunning) return;

    const timer = window.setInterval(() => {
      void loadLogs();
    }, 15000);

    return () => window.clearInterval(timer);
  }, [logs, loadLogs]);

  const handleSaveSchedule = async () => {
    const match = /^(\d{2}):(\d{2})$/.exec(scheduleTime);
    if (!match) {
      setScheduleMessage(t("admin.lmsSync.scheduleInvalidTime"));
      return;
    }

    const hour = Number(match[1]);
    const minute = Number(match[2]);
    if (hour > 23 || minute > 59) {
      setScheduleMessage(t("admin.lmsSync.scheduleInvalidTime"));
      return;
    }

    try {
      setSavingSchedule(true);
      setScheduleMessage("");
      setError("");
      const data = await saveLmsSyncSchedule({
        enabled: scheduleEnabled,
        hour,
        minute,
      });
      setSchedule(data);
      setScheduleTime(data.time);
      setScheduleEnabled(data.enabled);
      setScheduleMessage(t("admin.lmsSync.scheduleSaved"));
    } catch (err) {
      setScheduleMessage(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setSavingSchedule(false);
    }
  };

  const handleRunSync = async () => {
    try {
      setSyncing(true);
      setError("");
      await runLmsSync(false);
      await loadLogs();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("admin.lmsSync.runFailed"));
    } finally {
      setSyncing(false);
    }
  };

  const latest = logs[0];

  if (loading) {
    return (
      <div className="p-10 text-white flex justify-center mt-20">
        <div className="animate-spin w-10 h-10 border-4 border-cyan-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="p-10 text-white">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-4xl font-black bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
            {t("admin.lmsSync.title")}
          </h1>
          <p className="text-white/50 mt-2">
            {t("admin.lmsSync.subtitle")} {t("admin.lmsSync.refreshHint")}
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => void handleRunSync()}
            disabled={syncing || logs.some((log) => log.status === "running")}
            className="px-5 py-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 hover:bg-emerald-500/20 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {syncing ? t("admin.lmsSync.running") : t("admin.lmsSync.runNow")}
          </button>
          <button
            type="button"
            onClick={() => {
              setLoading(true);
              void loadLogs().finally(() => setLoading(false));
            }}
            disabled={syncing}
            className="px-5 py-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 hover:bg-cyan-500/20 transition disabled:opacity-50"
          >
            {t("common.refresh")}
          </button>
        </div>
      </div>

      <div className="mt-8 rounded-3xl border border-white/10 bg-white/[0.02] p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold">{t("admin.lmsSync.scheduleTitle")}</h2>
            <p className="text-white/50 text-sm mt-2">{t("admin.lmsSync.scheduleSubtitle")}</p>
            {schedule?.next_run_at && scheduleEnabled ? (
              <p className="text-cyan-300 text-sm mt-3">
                {t("admin.lmsSync.nextRun")}: {formatDateTime(schedule.next_run_at)} ({schedule.timezone})
              </p>
            ) : (
              <p className="text-white/40 text-sm mt-3">{t("admin.lmsSync.scheduleDisabled")}</p>
            )}
            <p className="text-white/35 text-xs mt-2">{t("admin.lmsSync.scheduleHint")}</p>
          </div>

          <div className="flex flex-wrap items-end gap-4">
            <label className="flex items-center gap-3 text-sm text-white/80">
              <input
                type="checkbox"
                checked={scheduleEnabled}
                onChange={(e) => setScheduleEnabled(e.target.checked)}
                className="h-4 w-4 rounded border-white/20 bg-white/5"
              />
              {t("admin.lmsSync.scheduleEnabled")}
            </label>

            <label className="flex flex-col gap-2 text-sm text-white/70">
              {t("admin.lmsSync.scheduleTime")}
              <input
                type="time"
                value={scheduleTime}
                onChange={(e) => setScheduleTime(e.target.value)}
                className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white outline-none focus:border-cyan-500 transition"
              />
            </label>

            <button
              type="button"
              onClick={() => void handleSaveSchedule()}
              disabled={savingSchedule}
              className="px-5 py-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 hover:bg-indigo-500/20 transition disabled:opacity-50"
            >
              {savingSchedule ? t("common.saving") : t("admin.lmsSync.scheduleSave")}
            </button>
          </div>
        </div>

        {scheduleMessage && (
          <div className="mt-4 rounded-2xl border border-cyan-500/20 bg-cyan-500/10 px-4 py-3 text-cyan-100 text-sm">
            {scheduleMessage}
          </div>
        )}
      </div>

      {latest && (
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded-3xl border border-white/10 bg-white/[0.02] p-6">
            <p className="text-white/50 text-sm">{t("admin.lmsSync.lastRun")}</p>
            <p className="text-xl font-bold mt-2">{formatDateTime(latest.started_at)}</p>
            <div className="mt-3">
              <StatusBadge status={latest.status} t={t} />
            </div>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.02] p-6">
            <p className="text-white/50 text-sm">{t("admin.lmsSync.studentsSummary")}</p>
            <p className="text-xl font-bold mt-2">
              +{latest.students_created} / ~{latest.students_updated}
            </p>
            <p className="text-white/40 text-sm mt-2">
              {t("admin.lmsSync.studentsSkipped")}: {latest.students_skipped}
            </p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.02] p-6">
            <p className="text-white/50 text-sm">{t("admin.lmsSync.transcriptsSummary")}</p>
            <p className="text-xl font-bold mt-2">
              +{latest.transcripts_created} / ~{latest.transcripts_updated}
            </p>
            <p className="text-white/40 text-sm mt-2">
              {t("admin.lmsSync.duration")}: {formatDuration(latest.duration_seconds)}
            </p>
          </div>
        </div>
      )}

      <div className="flex flex-wrap gap-4 mt-8">
        <select
          value={statusFilter}
          onChange={(e) => {
            setLoading(true);
            setStatusFilter(e.target.value);
          }}
          className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white outline-none focus:border-cyan-500 transition"
        >
          <option value="all">{t("admin.lmsSync.filterAll")}</option>
          <option value="running">{t("admin.lmsSync.statusRunning")}</option>
          <option value="success">{t("admin.lmsSync.statusSuccess")}</option>
          <option value="failed">{t("admin.lmsSync.statusFailed")}</option>
        </select>
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
                <th className="p-5">{t("admin.lmsSync.startedAt")}</th>
                <th className="p-5">{t("admin.lmsSync.finishedAt")}</th>
                <th className="p-5">{t("admin.lmsSync.duration")}</th>
                <th className="p-5">{t("admin.lmsSync.status")}</th>
                <th className="p-5">{t("admin.lmsSync.studentsCreated")}</th>
                <th className="p-5">{t("admin.lmsSync.studentsUpdated")}</th>
                <th className="p-5">{t("admin.lmsSync.transcriptsCreated")}</th>
                <th className="p-5">{t("admin.lmsSync.transcriptsUpdated")}</th>
                <th className="p-5">{t("admin.lmsSync.error")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={9} className="p-10 text-center text-white/40">
                    {t("admin.lmsSync.noLogs")}
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <Fragment key={log.id}>
                    <tr className="hover:bg-white/5 transition">
                      <td className="p-5">{formatDateTime(log.started_at)}</td>
                      <td className="p-5">{formatDateTime(log.finished_at)}</td>
                      <td className="p-5">{formatDuration(log.duration_seconds)}</td>
                      <td className="p-5">
                        <StatusBadge status={log.status} t={t} />
                      </td>
                      <td className="p-5">{log.students_created}</td>
                      <td className="p-5">{log.students_updated}</td>
                      <td className="p-5">{log.transcripts_created}</td>
                      <td className="p-5">{log.transcripts_updated}</td>
                      <td className="p-5">
                        {log.error_message ? (
                          <button
                            type="button"
                            onClick={() =>
                              setExpandedId(expandedId === log.id ? null : log.id)
                            }
                            className="text-rose-300 hover:text-rose-200 underline"
                          >
                            {t("common.view")}
                          </button>
                        ) : (
                          "—"
                        )}
                      </td>
                    </tr>
                    {expandedId === log.id && log.error_message && (
                      <tr className="bg-rose-500/5">
                        <td colSpan={9} className="p-5 text-rose-200 whitespace-pre-wrap">
                          {log.error_message}
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
