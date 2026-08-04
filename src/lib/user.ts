import { getMe } from "@/lib/api";

export async function getUserData(_uid: string) {
  return getMe();
}
