"use client";

import { useEffect, useState, useRef } from "react";
import { useTranslations } from "@/hooks/useTranslations";
import { useAuth } from "@/context/AuthContext";
import {
  getConversations,
  getMessages,
  sendMessage,
  startConversation,
} from "@/lib/api";
import type { ApiConversation, ApiMessage } from "@/lib/api";
import Sidebar from "@/app/components/dashboard/Sidebar";

export default function MessagesPage() {
  const { t } = useTranslations();
  const { user } = useAuth();
  const [conversations, setConversations] = useState<ApiConversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<number | null>(null);
  const [messages, setMessages] = useState<ApiMessage[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    if (activeConversation) {
      loadMessages(activeConversation);
    }
  }, [activeConversation]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadConversations = async () => {
    try {
      const data = await getConversations();
      setConversations(data);
      if (data.length > 0 && !activeConversation) {
        setActiveConversation(data[0].id);
      }
    } catch (err) {
      console.error("Load conversations error:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async (conversationId: number) => {
    try {
      const data = await getMessages(conversationId);
      setMessages(data);
    } catch (err) {
      console.error("Load messages error:", err);
    }
  };

  const handleSend = async () => {
    if (!newMessage.trim() || !activeConversation || sending) return;

    setSending(true);
    try {
      const msg = await sendMessage(activeConversation, newMessage.trim());
      setMessages((prev) => [...prev, msg]);
      setNewMessage("");
      loadConversations();
    } catch (err) {
      console.error("Send message error:", err);
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const activeChat = conversations.find((c) => c.id === activeConversation);

  return (
    <main className="min-h-screen bg-[#030712] text-white flex">
      <Sidebar />

      <div className="flex-1 flex overflow-hidden">
        {/* Conversations Sidebar */}
        <div className="w-80 border-r border-white/10 flex flex-col">
          <div className="p-4 border-b border-white/10">
            <h2 className="text-xl font-bold">{t("messaging.title")}</h2>
          </div>

          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-white/40">{t("common.loading")}</div>
            ) : conversations.length === 0 ? (
              <div className="p-6 text-center">
                <div className="text-4xl mb-3">💬</div>
                <p className="text-white/40 text-sm">{t("messaging.noConversations")}</p>
                <p className="text-white/30 text-xs mt-1">{t("messaging.noConversationsDesc")}</p>
              </div>
            ) : (
              conversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => setActiveConversation(conv.id)}
                  className={`w-full p-4 flex items-center gap-3 border-b border-white/5 hover:bg-white/5 transition-colors text-left ${
                    activeConversation === conv.id ? "bg-indigo-500/10 border-l-2 border-l-indigo-500" : ""
                  }`}
                >
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-sm font-bold flex-shrink-0">
                    {conv.participant?.name?.charAt(0)?.toUpperCase() || "?"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-sm truncate">
                        {conv.participant?.name || t("common.unknown")}
                      </span>
                      {conv.unread_count > 0 && (
                        <span className="bg-indigo-500 text-white text-xs rounded-full px-2 py-0.5 ml-2 flex-shrink-0">
                          {conv.unread_count}
                        </span>
                      )}
                    </div>
                    <p className="text-white/40 text-xs truncate mt-0.5">
                      {conv.last_message || t("messaging.noMessages")}
                    </p>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {activeConversation && activeChat ? (
            <>
              {/* Chat Header */}
              <div className="p-4 border-b border-white/10 flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center font-bold">
                  {activeChat.participant?.name?.charAt(0)?.toUpperCase() || "?"}
                </div>
                <div>
                  <p className="font-bold">{activeChat.participant?.name}</p>
                  <p className="text-xs text-white/40 capitalize">
                    {activeChat.participant?.role}
                  </p>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg) => {
                  const isMine = msg.sender_id === user?.id;
                  return (
                    <div key={msg.id} className={`flex ${isMine ? "justify-end" : "justify-start"}`}>
                      <div
                        className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                          isMine
                            ? "bg-indigo-600 text-white"
                            : "bg-white/10 text-white"
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                        <p className={`text-xs mt-1 ${isMine ? "text-white/60" : "text-white/30"}`}>
                          {new Date(msg.created_at).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </p>
                      </div>
                    </div>
                  );
                })}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="p-4 border-t border-white/10">
                <div className="flex gap-3">
                  <input
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder={t("messaging.typeMessage")}
                    className="flex-1 p-3 rounded-2xl bg-white/5 border border-white/10 focus:border-indigo-500 focus:outline-none transition-colors text-sm"
                  />
                  <button
                    onClick={handleSend}
                    disabled={!newMessage.trim() || sending}
                    className="px-6 py-3 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 font-bold text-sm transition-all disabled:opacity-50"
                  >
                    {t("messaging.send")}
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-white/30">
              <div className="text-center">
                <div className="text-6xl mb-4">💬</div>
                <p className="text-lg">{t("messaging.noMessages")}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
