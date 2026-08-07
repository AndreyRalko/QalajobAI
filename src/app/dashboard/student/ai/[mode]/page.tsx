"use client";

import { notFound, useParams } from "next/navigation";
import ResumeWorkspace from "@/app/components/dashboard/ResumeWorkspace";
import { workspaceModeFromSlug } from "@/lib/workspace-routes";

export default function WorkspaceModePage() {
  const params = useParams();
  const slug = String(params.mode || "");
  const mode = workspaceModeFromSlug(slug);

  if (!mode) {
    notFound();
  }

  return <ResumeWorkspace mode={mode} />;
}
