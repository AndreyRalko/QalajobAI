"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "@/hooks/useTranslations";
import { getUsers, deleteUser, banUser, unbanUser } from "@/lib/api";

const PAGE_SIZE = 25;

interface UserData {
  id: number;
  login?: string;
  name?: string;
  email?: string;
  role?: string;
  first_name?: string;
  last_name?: string;
  is_active?: boolean;
  date_joined?: string;
  created_at?: string;
  is_banned?: boolean;
}

function displayName(user: UserData): string {
  const fullName = user.name?.trim()
    || `${user.first_name || ""} ${user.last_name || ""}`.trim();
  return fullName || user.login || "";
}

export default function AdminUsersPage() {
  const { t } = useTranslations();

  const [users, setUsers] = useState<UserData[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [roleFilter, setRoleFilter] = useState("all");
  const [selectedUser, setSelectedUser] = useState<UserData | null>(null);
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  const loadUsers = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getUsers({
        page,
        search,
        role: roleFilter,
      });
      setUsers(data.results || []);
      setTotalCount(data.count || 0);
      setTotalPages(Math.max(1, Math.ceil((data.count || 0) / PAGE_SIZE)));
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, [page, search, roleFilter]);

  useEffect(() => {
    void loadUsers();
  }, [loadUsers]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSearch(searchInput);
      setPage(1);
    }, 350);
    return () => window.clearTimeout(timer);
  }, [searchInput]);

  const handleDeleteUser = async (userId: number) => {
    const confirmed = window.confirm(t("admin.users.confirmDelete") || "Delete this user?");
    if (!confirmed) return;

    try {
      await deleteUser(userId.toString());
      await loadUsers();
    } catch (error) {
      console.error(error);
    }
  };

  const toggleBanUser = async (userId: number, currentStatus: boolean) => {
    try {
      if (currentStatus) {
        await unbanUser(userId.toString());
      } else {
        await banUser(userId.toString());
      }

      setUsers((prev) =>
        prev.map((user) =>
          user.id === userId
            ? {
                ...user,
                is_banned: !currentStatus,
              }
            : user
        )
      );
    } catch (error) {
      console.error(error);
    }
  };

  const pageStart = totalCount === 0 ? 0 : (page - 1) * PAGE_SIZE + 1;
  const pageEnd = Math.min(page * PAGE_SIZE, totalCount);

  if (loading && users.length === 0) {
    return (
      <div className="p-10 text-white flex justify-center mt-20">
        <div className="animate-spin w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="p-10 text-white">
      <h1 className="text-4xl font-black bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
        {t("admin.users.title")}
      </h1>
      <p className="text-white/50 mt-2">
        {t("admin.users.total")}: {totalCount}
      </p>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mt-8">
        <input
          type="text"
          placeholder={t("admin.users.searchPlaceholder")}
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white w-80 outline-none focus:border-indigo-500 transition"
        />

        <select
          value={roleFilter}
          onChange={(e) => {
            setRoleFilter(e.target.value);
            setPage(1);
          }}
          className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:border-indigo-500 outline-none transition"
        >
          <option value="all">{t("admin.users.allRoles")}</option>
          <option value="student">{t("admin.users.studentRole")}</option>
          <option value="employer">{t("admin.users.employerRole")}</option>
        </select>
      </div>

      {/* Users Table */}
      <div className="mt-10 rounded-3xl overflow-hidden border border-white/10 bg-white/[0.02]">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-white/5 text-white/50 font-medium">
              <tr>
                <th className="p-5">{t("admin.users.name")}</th>
                <th className="p-5">{t("admin.users.email")}</th>
                <th className="p-5">{t("admin.users.role")}</th>
                <th className="p-5">{t("admin.users.status")}</th>
                <th className="p-5">{t("admin.users.registered")}</th>
                <th className="p-5 text-right">{t("admin.users.actions")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {loading ? (
                <tr>
                  <td colSpan={6} className="p-10 text-center text-white/40">
                    {t("common.loading")}
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-10 text-center text-white/40">
                    {t("common.noResults")}
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id} className="hover:bg-white/5 transition">
                    <td className="p-5 font-medium">
                      {displayName(user) || t("admin.users.noName")}
                      {user.login && displayName(user) !== user.login ? (
                        <p className="text-xs text-white/40 mt-1">{user.login}</p>
                      ) : null}
                    </td>
                    <td className="p-5 text-white/70">{user.email || "—"}</td>
                    <td className="p-5">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          user.role === "employer"
                            ? "bg-purple-500/20 text-purple-400 border border-purple-500/20"
                            : "bg-cyan-500/20 text-cyan-400 border border-cyan-500/20"
                        }`}
                      >
                        {user.role}
                      </span>
                    </td>
                    <td className="p-5">
                      {user.is_banned ? (
                        <span className="bg-red-500/20 border border-red-500/30 text-red-400 px-2.5 py-1 rounded-lg text-xs font-bold">
                          {t("admin.users.bannedBadge")}
                        </span>
                      ) : user.is_active ? (
                        <span className="bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 px-2.5 py-1 rounded-lg text-xs font-bold">
                          {t("admin.users.activeBadge")}
                        </span>
                      ) : (
                        <span className="bg-white/10 border border-white/20 text-white/50 px-2.5 py-1 rounded-lg text-xs font-bold">
                          {t("admin.users.inactiveBadge")}
                        </span>
                      )}
                    </td>
                    <td className="p-5 text-white/50">
                      {user.date_joined || user.created_at
                        ? new Date(user.date_joined || user.created_at!).toLocaleDateString()
                        : t("admin.users.na")}
                    </td>
                    <td className="p-5">
                      <div className="flex gap-2 justify-end">
                        <button
                          onClick={() => setSelectedUser(user)}
                          className="bg-white/10 hover:bg-white/20 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition"
                        >
                          {t("common.view")}
                        </button>
                        <button
                          onClick={() => toggleBanUser(user.id, user.is_banned || false)}
                          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                            user.is_banned
                              ? "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30"
                              : "bg-orange-500/20 text-orange-400 hover:bg-orange-500/30"
                          }`}
                        >
                          {user.is_banned ? t("admin.users.unban") : t("admin.users.ban")}
                        </button>
                        <button
                          onClick={() => handleDeleteUser(user.id)}
                          className="bg-red-500/20 text-red-400 hover:bg-red-500/30 px-3 py-1.5 rounded-lg text-xs font-medium transition"
                        >
                          {t("common.delete")}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {totalCount > 0 && (
          <div className="flex flex-wrap items-center justify-between gap-4 px-5 py-4 border-t border-white/10 bg-white/[0.02]">
            <p className="text-sm text-white/50">
              {t("admin.users.showing")} {pageStart}–{pageEnd} {t("admin.users.of")} {totalCount}
            </p>
            <div className="flex items-center gap-2">
              <button
                type="button"
                disabled={page <= 1 || loading}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-medium transition"
              >
                {t("admin.users.prevPage")}
              </button>
              <span className="text-sm text-white/60 px-2">
                {t("admin.users.page")} {page} {t("admin.users.of")} {totalPages}
              </span>
              <button
                type="button"
                disabled={page >= totalPages || loading}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-medium transition"
              >
                {t("admin.users.nextPage")}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* User Details Modal */}
      {selectedUser && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-[#0b1120] border border-white/10 rounded-3xl p-8 w-[500px] max-w-full shadow-2xl animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">{t("admin.users.details")}</h2>
              <button
                onClick={() => setSelectedUser(null)}
                className="text-white/40 hover:text-white transition w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/10"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div className="bg-white/5 p-4 rounded-2xl border border-white/5">
                <p className="text-xs text-white/40 mb-1">{t("admin.users.idLabel")}</p>
                <p className="font-mono">{selectedUser.id}</p>
              </div>
              <div className="bg-white/5 p-4 rounded-2xl border border-white/5">
                <p className="text-xs text-white/40 mb-1">{t("admin.users.emailLabel")}</p>
                <p>{selectedUser.email}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white/5 p-4 rounded-2xl border border-white/5">
                  <p className="text-xs text-white/40 mb-1">{t("admin.users.roleLabel")}</p>
                  <p className="capitalize">{selectedUser.role}</p>
                </div>
                <div className="bg-white/5 p-4 rounded-2xl border border-white/5">
                  <p className="text-xs text-white/40 mb-1">{t("admin.users.statusLabel")}</p>
                  <p>{selectedUser.is_banned ? t("admin.users.statusBanned") + " 🔴" : selectedUser.is_active ? t("admin.users.statusActive") + " 🟢" : t("admin.users.statusInactive") + " ⚪"}</p>
                </div>
              </div>
            </div>

            <div className="mt-8 flex justify-end">
               <button
                  onClick={() => setSelectedUser(null)}
                  className="px-6 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 transition font-medium"
                >
                  {t("admin.users.close")}
                </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
