"use client";

import { useState } from "react";
import {
  hhAdaptResume,
  hhGetVacancy,
  hhSearchVacancies,
  type HhVacancyDetail,
  type HhVacancyListItem,
} from "@/lib/api";
import { useTranslations } from "@/hooks/useTranslations";

type Props = {
  resumeDraft: string;
  onAdapted: (adaptedResume: string, notes: string) => void;
};

export default function HhJobsPanel({ resumeDraft, onAdapted }: Props) {
  const { t, locale } = useTranslations();
  const [query, setQuery] = useState("");
  const [urlOrId, setUrlOrId] = useState("");
  const [searching, setSearching] = useState(false);
  const [adapting, setAdapting] = useState(false);
  const [warning, setWarning] = useState("");
  const [items, setItems] = useState<HhVacancyListItem[]>([]);
  const [selected, setSelected] = useState<HhVacancyDetail | null>(null);
  const [notes, setNotes] = useState("");
  const [missing, setMissing] = useState<string[]>([]);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    setSearching(true);
    setError("");
    setWarning("");
    try {
      const data = await hhSearchVacancies({ text: query.trim() || "developer" });
      setItems(data.items || []);
      if (data.warning) setWarning(data.warning);
      if (data.demo) setWarning((prev) => prev || t("aiPage.hhDemoNotice"));
      setSelected(null);
    } catch (e) {
      console.error(e);
      setError(e instanceof Error ? e.message : t("aiPage.aiError"));
      setItems([]);
    } finally {
      setSearching(false);
    }
  };

  const openVacancy = async (id: string) => {
    setError("");
    try {
      const detail = await hhGetVacancy(id);
      setSelected(detail);
      setNotes("");
      setMissing([]);
    } catch (e) {
      console.error(e);
      setError(e instanceof Error ? e.message : t("aiPage.aiError"));
    }
  };

  const openByUrl = async () => {
    const value = urlOrId.trim();
    if (!value) return;
    // Extract id from URL client-side roughly; backend also parses
    const match = value.match(/vacancy\/(\d+|demo-[\w-]+)/i);
    const id = match?.[1] || value;
    await openVacancy(id);
  };

  const adapt = async () => {
    if (!selected?.id) return;
    setAdapting(true);
    setError("");
    try {
      const data = await hhAdaptResume({
        vacancyId: selected.id,
        resume: resumeDraft,
        language: locale,
        save: true,
      });
      setNotes(data.match_notes || "");
      setMissing(data.missing_skills || []);
      onAdapted(data.adapted_resume || data.document_draft || "", data.match_notes || "");
    } catch (e) {
      console.error(e);
      setError(e instanceof Error ? e.message : t("aiPage.aiError"));
    } finally {
      setAdapting(false);
    }
  };

  return (
    <div className="mt-4 grid lg:grid-cols-2 gap-4 flex-1 min-h-0">
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-4 md:p-5 flex flex-col min-h-[420px] lg:min-h-0">
        <h2 className="text-lg font-bold text-cyan-300 mb-3">{t("aiPage.hhSearchTitle")}</h2>

        <div className="flex gap-2 shrink-0">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("aiPage.hhSearchPlaceholder")}
            className="flex-1 px-4 py-2 rounded-2xl bg-white/5 border border-white/10 text-sm outline-none"
            onKeyDown={(e) => {
              if (e.key === "Enter") void handleSearch();
            }}
          />
          <button
            type="button"
            onClick={() => void handleSearch()}
            disabled={searching}
            className="px-4 py-2 rounded-2xl bg-cyan-500 text-black text-sm font-bold disabled:opacity-50"
          >
            {searching ? t("aiPage.hhSearching") : t("aiPage.hhSearch")}
          </button>
        </div>

        <div className="mt-3 flex gap-2 shrink-0">
          <input
            value={urlOrId}
            onChange={(e) => setUrlOrId(e.target.value)}
            placeholder={t("aiPage.hhUrlPlaceholder")}
            className="flex-1 px-4 py-2 rounded-2xl bg-white/5 border border-white/10 text-sm outline-none"
          />
          <button
            type="button"
            onClick={() => void openByUrl()}
            className="px-4 py-2 rounded-2xl border border-white/10 bg-white/5 text-sm text-white/80"
          >
            {t("aiPage.hhOpen")}
          </button>
        </div>

        {warning ? (
          <p className="mt-3 text-xs text-amber-300/90 bg-amber-500/10 border border-amber-500/20 rounded-2xl p-3">
            {warning}
          </p>
        ) : null}
        {error ? (
          <p className="mt-3 text-xs text-red-300 bg-red-500/10 border border-red-500/20 rounded-2xl p-3">
            {error}
          </p>
        ) : null}

        <div className="mt-4 flex-1 overflow-y-auto space-y-2 min-h-0">
          {items.length === 0 ? (
            <p className="text-white/40 text-sm">{t("aiPage.hhEmpty")}</p>
          ) : (
            items.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => void openVacancy(item.id)}
                className={`w-full text-left p-4 rounded-2xl border transition ${
                  selected?.id === item.id
                    ? "border-cyan-500/40 bg-cyan-500/10"
                    : "border-white/10 bg-white/5 hover:border-white/20"
                }`}
              >
                <p className="font-semibold text-sm">{item.name}</p>
                <p className="text-white/50 text-xs mt-1">
                  {[item.company, item.area, item.salary].filter(Boolean).join(" · ")}
                </p>
                {item.requirement ? (
                  <p className="text-white/40 text-xs mt-2 line-clamp-2">{item.requirement}</p>
                ) : null}
              </button>
            ))
          )}
        </div>
      </section>

      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-4 md:p-5 flex flex-col min-h-[420px] lg:min-h-0">
        <div className="flex items-center justify-between gap-3 mb-3 shrink-0">
          <h2 className="text-lg font-bold text-cyan-300">{t("aiPage.hhDetailTitle")}</h2>
          {selected ? (
            <button
              type="button"
              onClick={() => void adapt()}
              disabled={adapting}
              className="px-4 py-2 rounded-full bg-cyan-500 text-black text-sm font-bold disabled:opacity-50"
            >
              {adapting ? t("aiPage.hhAdapting") : t("aiPage.hhAdapt")}
            </button>
          ) : null}
        </div>

        {!selected ? (
          <p className="text-white/40 text-sm">{t("aiPage.hhSelectHint")}</p>
        ) : (
          <div className="flex-1 overflow-y-auto min-h-0 space-y-4 text-sm">
            <div>
              <h3 className="text-xl font-bold">{selected.name}</h3>
              <p className="text-white/50 mt-1">
                {[selected.company, selected.area, selected.salary]
                  .filter(Boolean)
                  .join(" · ")}
              </p>
              {selected.url ? (
                <a
                  href={selected.url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-block mt-2 text-cyan-300 text-xs hover:underline"
                >
                  {t("aiPage.hhOpenOnHh")}
                </a>
              ) : null}
            </div>

            {selected.skills?.length ? (
              <div className="flex flex-wrap gap-2">
                {selected.skills.map((skill) => (
                  <span
                    key={skill}
                    className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs text-white/70"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            ) : null}

            <div className="whitespace-pre-wrap text-white/70 leading-relaxed">
              {selected.description ||
                [selected.requirement, selected.responsibility]
                  .filter(Boolean)
                  .join("\n\n")}
            </div>

            {notes ? (
              <div className="rounded-2xl border border-cyan-500/20 bg-cyan-500/10 p-4">
                <p className="text-cyan-300 font-semibold text-xs uppercase tracking-wide">
                  {t("aiPage.hhMatchNotes")}
                </p>
                <p className="mt-2 text-white/80 whitespace-pre-wrap">{notes}</p>
              </div>
            ) : null}

            {missing.length ? (
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p className="text-white/50 text-xs uppercase tracking-wide">
                  {t("aiPage.hhMissingSkills")}
                </p>
                <p className="mt-2 text-white/80">{missing.join(", ")}</p>
              </div>
            ) : null}
          </div>
        )}
      </section>
    </div>
  );
}
