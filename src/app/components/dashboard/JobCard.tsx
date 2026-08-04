"use client";

import Link from "next/link";
import { saveJob } from "@/lib/savedJobs";

export default function JobCard({
  id,
  title,
  company,
  match,
}: {
  id: string;
  title: string;
  company: string;
  match: string;
}) {
  const handleSaveJob = async () => {
    try {
      await saveJob(id);

      alert("Job saved successfully ❤️");
    } catch (error) {
      console.error(error);

      alert("Please login first");
    }
  };

  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.02] p-6">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-bold text-xl">
            {title}
          </h3>

          <p className="text-white/50 mt-1">
            {company}
          </p>
        </div>

        <span className="text-green-400 font-bold">
          {match}
        </span>
      </div>

      <div className="flex gap-3 mt-6">
        <Link
          href={`/dashboard/student/jobs/${id}`}
          className="px-5 py-3 rounded-2xl bg-cyan-500 text-black font-bold hover:bg-cyan-400 transition"
        >
          View Job
        </Link>

        <button
          onClick={handleSaveJob}
          className="px-5 py-3 rounded-2xl bg-pink-500 text-white font-bold hover:bg-pink-400 transition"
        >
          ❤️ Save
        </button>
      </div>
    </div>
  );
}