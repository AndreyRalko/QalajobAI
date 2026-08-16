"use client";

import { useState } from "react";
import {
  hhGetVacancy,
  hhSearchVacancies,
  type HhVacancyListItem,
} from "@/lib/api";
import { useTranslations } from "@/hooks/useTranslations";

type Props = {
  onSelect: (vacancy: {
    title: string;
    company: string;
    description: string;
    url: string;
  }) => void;
};

export default function HhVacancyPicker({ onSelect }: Props) {
  const { t } = useTranslations();
  const [query, setQuery] = useState("");
  const [urlOrId, setUrlOrId] = useState("");
  const [searching, setSearching] = useState(false);
  const [items, setItems] = useState<HhVacancyListItem[]>([]);
  const [warning, setWarning] = useState("");
  const [error, setError] = useState("");
  const [pickedId, setPickedId] = useState("");

  const applyDetail = async (id: string) => {
    setError("");
    try {
      const detail = await hhGetVacancy(id);
      setPickedId(detail.id);
      const description = [
        detail.experience ? `Опыт: ${detail.experience}` : "",
        detail.employment ? `Занятость: ${detail.employment}` : "",
        detail.salary ? `Зарплата: ${detail.salary}` : "",
        detail.skills?.length ? `Навыки: ${detail.skills.join(", ")}` : "",
        detail.requirement ? `Требования:\n${detail.requirement}` : "",
        detail.responsibility
          ? `Обязанности:\n${detail.responsibility}`
          : "",
        detail.description || "",
        detail.url ? `Ссылка: ${detail.url}` : "",
      ]
        .filter(Boolean)
        .join("\n\n");
      onSelect({
        title: detail.name || "",
        company: detail.company || "",
        description,
        url: detail.url || "",
      });
    } catch (e) {
      console.error(e);
      setError(e instanceof Error ? e.message : t("aiPage.aiError"));
    }
  };

  const handleSearch = async () => {
    setSearching(true);
    setError("");
    setWarning("");
    try {
      const data = await hhSearchVacancies({
        text: query.trim() || "developer",
      });
      setItems(data.items || []);
      if (data.warning) setWarning(data.warning);
      if (data.demo) setWarning((prev) => prev || t("aiPage.hhDemoNotice"));
    } catch (e) {
      console.error(e);
      setError(e instanceof Error ? e.message : t("aiPage.aiError"));
      setItems([]);
    } finally {
      setSearching(false);
    }
  };

  const openByUrl = async () => {
    const value = urlOrId.trim();
    if (!value) return;
    const match = value.match(/vacancy\/(\d+|demo-[\w-]+)/i);
    const id = match?.[1] || value;
    await applyDetail(id);
  };

  return (
    <div className="mb-4 space-y-3">
      <div className="flex gap-2">
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
          className="px-4 py-2 rounded-2xl bg-white/10 border border-white/10 text-sm font-medium disabled:opacity-50"
        >
          {searching ? t("aiPage.hhSearching") : t("aiPage.hhSearch")}
        </button>
      </div>

      <div className="flex gap-2">
        <input
          value={urlOrId}
          onChange={(e) => setUrlOrId(e.target.value)}
          placeholder={t("aiPage.hhUrlPlaceholder")}
          className="flex-1 px-4 py-2 rounded-2xl bg-white/5 border border-white/10 text-sm outline-none"
          onKeyDown={(e) => {
            if (e.key === "Enter") void openByUrl();
          }}
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
        <p className="text-xs text-amber-300/90 bg-amber-500/10 border border-amber-500/20 rounded-2xl p-3">
          {warning}
        </p>
      ) : null}
      {error ? (
        <p className="text-xs text-red-300 bg-red-500/10 border border-red-500/20 rounded-2xl p-3">
          {error}
        </p>
      ) : null}

      {items.length ? (
        <div className="max-h-56 overflow-y-auto space-y-2">
          {items.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => void applyDetail(item.id)}
              className={`w-full text-left p-3 rounded-2xl border transition ${
                pickedId === item.id
                  ? "border-cyan-500/40 bg-cyan-500/10"
                  : "border-white/10 bg-white/5 hover:border-white/20"
              }`}
            >
              <p className="font-semibold text-sm">{item.name}</p>
              <p className="text-white/50 text-xs mt-1">
                {[item.company, item.area, item.salary]
                  .filter(Boolean)
                  .join(" · ")}
              </p>
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
