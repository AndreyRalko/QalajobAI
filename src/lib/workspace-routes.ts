import type { WorkspaceMode } from "@/lib/api";

export const WORKSPACE_MODE_SLUGS: Record<WorkspaceMode, string> = {
  resume: "resume",
  cover_letter: "cover-letter",
  interview: "interview",
  mock_interview: "mock-interview",
};

const SLUG_TO_MODE = Object.fromEntries(
  Object.entries(WORKSPACE_MODE_SLUGS).map(([mode, slug]) => [slug, mode])
) as Record<string, WorkspaceMode>;

export function workspaceModeFromSlug(slug: string): WorkspaceMode | null {
  return SLUG_TO_MODE[slug] ?? null;
}

export function workspaceHref(mode: WorkspaceMode): string {
  return `/dashboard/student/ai/${WORKSPACE_MODE_SLUGS[mode]}`;
}

export const WORKSPACE_MODES: WorkspaceMode[] = [
  "resume",
  "cover_letter",
  "interview",
  "mock_interview",
];
