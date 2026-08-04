import { getResume as getResumeApi, saveResume as saveResumeApi } from "@/lib/api";

export async function getResume(_uid?: string) {
  const data = await getResumeApi();
  return { ...data, resume: data.content };
}

export async function saveResume(
  uidOrData: string | Record<string, unknown>,
  data?: Record<string, unknown> | string
) {
  let content = "";
  if (typeof uidOrData === "string") {
    if (typeof data === "string") content = data;
    else content = (data?.resume as string) || (data?.content as string) || "";
  } else {
    content = (uidOrData.content as string) || (uidOrData.resume as string) || "";
  }
  return saveResumeApi({ content });
}

export async function getUserResume() {
  return getResume();
}

export async function updateUserResume(content: string) {
  return saveResume(content);
}
