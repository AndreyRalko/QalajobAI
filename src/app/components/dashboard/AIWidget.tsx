"use client";

import Link from "next/link";

export default function AIWidget() {
  return (
    <div className="rounded-3xl border border-cyan-500/20 bg-cyan-500/5 p-6">
      <h3 className="text-2xl font-bold">🤖 AI Resume Assistant</h3>

      <p className="text-white/50 mt-2">
        Build and improve your resume with a guided AI conversation.
      </p>

      <Link
        href="/dashboard/student/ai"
        className="mt-6 inline-flex h-12 items-center justify-center rounded-2xl bg-cyan-500 px-6 font-bold text-black hover:bg-cyan-400 transition"
      >
        Open resume assistant
      </Link>
    </div>
  );
}
