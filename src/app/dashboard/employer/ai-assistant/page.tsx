"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { useTranslations } from "@/hooks/useTranslations";
import { aiAssistant } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function EmployerAIAssistantPage() {
  const { t, locale } = useTranslations();
  const [question, setQuestion] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [messages, setMessages] =
    useState<Message[]>([]);

  const handleAsk = async () => {
    if (!question.trim()) return;

    const userQuestion = question;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const data = await aiAssistant(userQuestion, messages, locale);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            data.reply ||
            "No response from AI",
        },
      ]);
    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "AI Assistant Error ❌",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (

      <div className="flex-1 p-10">

        <h1 className="text-5xl font-black">
          🤖 {t("employerAiAssistant.title")}
        </h1>

        <p className="text-white/50 mt-3">
          {t("employerAiAssistant.subtitle")}
        </p>

        {/* QUICK ACTIONS */}

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mt-10">

          <button
            onClick={() =>
              setQuestion(
                "Generate vacancy for Frontend Developer"
              )
            }
            className="p-5 rounded-3xl bg-white/5 border border-white/10 hover:border-cyan-500 transition text-left"
          >
            <div className="text-3xl">
              💼
            </div>

            <h3 className="font-bold mt-3">
              Vacancy Generator
            </h3>

            <p className="text-white/50 text-sm mt-2">
              Create complete job
              descriptions
            </p>
          </button>

          <button
            onClick={() =>
              setQuestion(
                "Generate interview questions for React Developer"
              )
            }
            className="p-5 rounded-3xl bg-white/5 border border-white/10 hover:border-cyan-500 transition text-left"
          >
            <div className="text-3xl">
              🎤
            </div>

            <h3 className="font-bold mt-3">
              Interview Questions
            </h3>

            <p className="text-white/50 text-sm mt-2">
              Generate technical
              interview questions
            </p>
          </button>

          <button
            onClick={() =>
              setQuestion(
                "Evaluate Junior Frontend candidate"
              )
            }
            className="p-5 rounded-3xl bg-white/5 border border-white/10 hover:border-cyan-500 transition text-left"
          >
            <div className="text-3xl">
              📊
            </div>

            <h3 className="font-bold mt-3">
              Candidate Evaluation
            </h3>

            <p className="text-white/50 text-sm mt-2">
              Analyze candidate
              strengths and weaknesses
            </p>
          </button>

          <button
            onClick={() =>
              setQuestion(
                "Suggest hiring strategy for IT company"
              )
            }
            className="p-5 rounded-3xl bg-white/5 border border-white/10 hover:border-cyan-500 transition text-left"
          >
            <div className="text-3xl">
              🚀
            </div>

            <h3 className="font-bold mt-3">
              Hiring Strategy
            </h3>

            <p className="text-white/50 text-sm mt-2">
              Get recruitment advice
            </p>
          </button>

        </div>

        {/* CHAT */}

        <div className="mt-10 rounded-3xl border border-white/10 bg-white/5 p-6 h-[150px] overflow-y-auto">

          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center text-white/40">

              {t("employerAiAssistant.noMessages")}

            </div>
          ) : (
            messages.map(
              (
                message,
                index
              ) => (
                <div
                  key={index}
                  className={`mb-4 ${
                    message.role ===
                    "user"
                      ? "flex justify-end"
                      : "flex justify-start"
                  }`}
                >
                  <div
  className={`max-w-[75%] p-4 rounded-3xl overflow-x-auto ${
    message.role === "user"
      ? "bg-cyan-500 text-black"
      : "bg-white/10"
  }`}
>
  <ReactMarkdown>
    {message.content}
  </ReactMarkdown>
</div>
                </div>
              )
            )
          )}

          {loading && (
            <div className="flex justify-start">

              <div className="bg-white/10 rounded-3xl p-4">

                🤖 {t("employerAiAssistant.sending")}

              </div>

            </div>
          )}

        </div>

        {/* INPUT */}

        <div className="flex gap-4 mt-6">

          <input
            value={question}
            onChange={(e) =>
              setQuestion(
                e.target.value
              )
            }
            placeholder={t("employerAiAssistant.placeholder")}
            className="flex-1 p-5 rounded-3xl bg-white/5 border border-white/10 outline-none"
            onKeyDown={(e) => {
              if (
                e.key ===
                "Enter"
              ) {
                handleAsk();
              }
            }}
          />

          <button
            onClick={
              handleAsk
            }
            disabled={
              loading
            }
            className="px-10 rounded-3xl bg-cyan-500 text-black font-bold hover:bg-cyan-400 disabled:opacity-50"
          >
            {loading
              ? t("employerAiAssistant.sending")
              : t("employerAiAssistant.send")}
          </button>

        </div>

      </div>
  );
}
