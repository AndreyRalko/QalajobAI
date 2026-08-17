"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { useTranslations } from "@/hooks/useTranslations";
import {
  aiJobRecommendations,
  type ApiJobRecommendation,
  type ApiJobRecommendationsResult,
  type WorkspaceMode,
} from "@/lib/api";
import {
  buildVacancyDescription,
  saveVacancyContext,
} from "@/lib/vacancy-context-storage";
import { workspaceHref, WORKSPACE_MODES } from "@/lib/workspace-routes";

const MODULE_ICONS: Record<WorkspaceMode, string> = {
  resume: "📄",
  cover_letter: "✉️",
  interview: "💼",
  mock_interview: "🎙️",
};

export default function StudentJobsPage() {
  const { t, lang } = useTranslations();
  const [jobInterests, setJobInterests] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<ApiJobRecommendation[]>(
    []
  );
  const [hhSearch, setHhSearch] = useState<
    ApiJobRecommendationsResult["hh_search"] | null
  >(null);
  const [searched, setSearched] = useState(false);

  const handleSubmit = async () => {
    const interests = jobInterests.trim();
    if (!interests) {
      setError(t("studentJobs.interestsRequired"));
      return;
    }

    setLoading(true);
    setError(null);
    setSearched(true);
    try {
      const data = await aiJobRecommendations({
        job_interests: interests,
        limit: 10,
        language: lang === "kz" ? "kk" : lang,
      });
      setRecommendations(data.recommendations ?? []);
      setHhSearch(data.hh_search ?? null);
    } catch (err) {
      console.error(err);
      setRecommendations([]);
      setHhSearch(null);
      setError(t("studentJobs.loadError"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 md:p-10">
      <h1 className="text-5xl font-black">{t("studentJobs.title")}</h1>
      <p className="text-white/50 mt-2">{t("studentJobs.subtitle")}</p>

      <div className="mt-10 max-w-3xl rounded-3xl border border-white/10 bg-white/[0.02] p-6">
        <label htmlFor="job-interests" className="block font-semibold text-lg">
          {t("studentJobs.interestsLabel")}
        </label>
        <p className="text-white/50 text-sm mt-1">
          {t("studentJobs.interestsHint")}
        </p>
        <textarea
          id="job-interests"
          value={jobInterests}
          onChange={(e) => setJobInterests(e.target.value)}
          placeholder={t("studentJobs.interestsPlaceholder")}
          rows={5}
          className="mt-4 w-full p-4 rounded-2xl bg-white/5 border border-white/10 outline-none focus:border-cyan-500/40 resize-y min-h-[140px]"
        />
        <button
          type="button"
          onClick={() => void handleSubmit()}
          disabled={loading || !jobInterests.trim()}
          className="mt-5 px-6 py-3 rounded-2xl bg-cyan-500 text-black font-bold disabled:opacity-50"
        >
          {loading ? t("studentJobs.loading") : t("studentJobs.search")}
        </button>
      </div>

      {error ? <p className="mt-6 text-red-400">{error}</p> : null}

      {hhSearch?.text ? (
        <div className="mt-6 max-w-3xl rounded-2xl border border-cyan-500/20 bg-cyan-500/10 p-4">
          <p className="text-cyan-400/80 text-sm">{t("studentJobs.hhQuery")}</p>
          <p className="font-semibold mt-1">{hhSearch.text}</p>
          {hhSearch.reasoning ? (
            <p className="text-white/50 text-sm mt-2">{hhSearch.reasoning}</p>
          ) : null}
          {hhSearch.demo ? (
            <p className="text-orange-300 text-sm mt-2">{t("studentJobs.hhDemo")}</p>
          ) : null}
        </div>
      ) : null}

      {loading ? (
        <p className="mt-10 text-white/50">{t("studentJobs.loading")}</p>
      ) : searched && recommendations.length === 0 && !error ? (
        <p className="mt-10 text-white/50">{t("studentJobs.noVacancies")}</p>
      ) : (
        <div className="mt-10 space-y-5">
          {recommendations.map((item) => (
            <RecommendationCard key={item.vacancy_id} item={item} t={t} />
          ))}
        </div>
      )}
    </div>
  );
}

function RecommendationCard({
  item,
  t,
}: {
  item: ApiJobRecommendation;
  t: (key: string) => string;
}) {
  const router = useRouter();
  const vacancy = item.vacancy;

  const openInModule = (mode: WorkspaceMode) => {
    saveVacancyContext({
      jobTitle: vacancy.name,
      company: vacancy.company,
      jobDescription: buildVacancyDescription(vacancy),
      url: vacancy.url,
    });
    router.push(workspaceHref(mode));
  };

  const moduleLabel = (mode: WorkspaceMode) => {
    if (mode === "resume") return t("student.menu.resume");
    if (mode === "cover_letter") return t("student.menu.coverLetter");
    if (mode === "interview") return t("student.menu.interview");
    return t("student.menu.mockInterview");
  };

  return (
    <article className="rounded-3xl border border-white/10 bg-white/[0.02] p-6">
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold">{vacancy.name}</h2>
          <p className="text-white/50 mt-1">
            {vacancy.company}
            {vacancy.area ? ` · ${vacancy.area}` : ""}
          </p>
          {vacancy.salary ? (
            <p className="text-cyan-400 mt-2 font-semibold">{vacancy.salary}</p>
          ) : null}
        </div>
        <div className="text-right">
          <p className="text-green-400 text-3xl font-black">{item.match_score}%</p>
          <p className="text-white/40 text-sm">{t("studentJobs.match")}</p>
        </div>
      </div>

      <p className="text-white/70 mt-4 leading-relaxed">{item.explanation}</p>

      {item.matching_skills.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {item.matching_skills.map((skill) => (
            <span
              key={skill}
              className="px-3 py-1 rounded-full bg-green-500/10 text-green-400 text-sm border border-green-500/20"
            >
              {skill}
            </span>
          ))}
        </div>
      )}

      {item.missing_skills.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {item.missing_skills.map((skill) => (
            <span
              key={skill}
              className="px-3 py-1 rounded-full bg-orange-500/10 text-orange-300 text-sm border border-orange-500/20"
            >
              {skill}
            </span>
          ))}
        </div>
      )}

      {vacancy.requirement ? (
        <p className="text-white/50 mt-4 text-sm line-clamp-3">
          {vacancy.requirement}
        </p>
      ) : null}

      <div className="mt-6 pt-5 border-t border-white/10">
        <p className="text-white/50 text-sm mb-3">{t("studentJobs.prepareWith")}</p>
        <div className="flex flex-wrap gap-2">
          {WORKSPACE_MODES.map((mode) => (
            <button
              key={mode}
              type="button"
              onClick={() => openInModule(mode)}
              className="px-4 py-2 rounded-2xl border border-white/10 bg-white/5 text-sm font-medium hover:bg-cyan-500/10 hover:border-cyan-500/30 hover:text-cyan-300 transition"
            >
              <span aria-hidden="true">{MODULE_ICONS[mode]} </span>
              {moduleLabel(mode)}
            </button>
          ))}
        </div>
      </div>

      {vacancy.url ? (
        <a
          href={vacancy.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block mt-5 px-5 py-3 rounded-2xl border border-white/10 text-white/80 font-semibold hover:bg-white/5 transition"
        >
          {t("studentJobs.openOnHh")}
        </a>
      ) : null}
    </article>
  );
}
