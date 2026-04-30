"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface SourceDoc {
  content: string;
  title: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: SourceDoc[];
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function ShamrockLogo({ size = 36 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 36 36" fill="none">
      <circle cx="18" cy="11" r="7.5" fill="#4a9e68" />
      <circle cx="11" cy="21.5" r="7.5" fill="#4a9e68" />
      <circle cx="25" cy="21.5" r="7.5" fill="#4a9e68" />
      <path d="M18 24 C18 28 16 31 15 34" stroke="#4a9e68" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}


export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const hasMessages = messages.length > 0;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  async function handleSubmit(e?: React.FormEvent) {
    e?.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, top_k: 4 }),
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data: { answer: string; sources: SourceDoc[] } = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.answer, sources: data.sources },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  const inputBar = (
    <div
      style={{ background: "#2a2a27", borderRadius: "1.25rem", border: "1px solid rgba(255,255,255,0.08)" }}
      className="flex flex-col px-5 pt-4 pb-4 gap-2 shadow-lg"
    >
      <textarea
        ref={textareaRef}
        rows={1}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={loading}
        placeholder={hasMessages ? "Write a message..." : "How can I help you today?"}
        style={{
          background: "transparent",
          color: "#e8e8e5",
          resize: "none",
          outline: "none",
          fontSize: "1rem",
          lineHeight: "1.6",
          fontFamily: "var(--font-quicksand), sans-serif",
        }}
        className="w-full placeholder-[#9b9b97] disabled:opacity-50 overflow-y-auto"
      />
      <div className="flex items-center justify-end">
        <SendButton onSend={handleSubmit} active={!!input.trim() && !loading} />
      </div>
    </div>
  );

  if (!hasMessages) {
    return (
      <div
        className="flex flex-col items-center justify-center h-screen px-4"
        style={{ background: "#1c1c1a", color: "#e8e8e5" }}
      >
        <div className="w-full max-w-2xl flex flex-col items-center gap-8">
          <div className="flex flex-col items-center gap-4">
            <ShamrockLogo size={64} />
            <div className="text-center">
              <h1 className="text-5xl font-normal tracking-tight" style={{ color: "#e8e8e5", fontFamily: "var(--font-source-serif), serif" }}>
                Dia duit!
              </h1>
              <p className="mt-1.5 text-lg" style={{ color: "#8c8c89", fontFamily: "var(--font-quicksand), sans-serif" }}>
                Ask anything about the Irish language
              </p>
            </div>
          </div>
          <div className="w-full">
            {inputBar}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen" style={{ background: "#1c1c1a", color: "#e8e8e5" }}>
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
          {messages.map((msg, i) => (
            <MessageBubble key={i} message={msg} />
          ))}
          {loading && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>
      </main>

      <footer className="px-4 pb-5 pt-2 shrink-0">
        <div className="max-w-2xl mx-auto">
          {inputBar}
        </div>
      </footer>
    </div>
  );
}

function SendButton({ onSend, active }: { onSend: () => void; active: boolean }) {
  const [hovered, setHovered] = useState(false);

  let bg = "rgba(255,255,255,0.08)";
  if (active) bg = hovered ? "#3a8556" : "#4a9e68";

  return (
    <button
      type="button"
      onClick={onSend}
      disabled={!active}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        background: bg,
        color: active ? "#fff" : "#6b6b68",
        borderRadius: "50%",
        width: "2rem",
        height: "2rem",
        transition: "background 0.15s, color 0.15s",
      }}
      className="flex items-center justify-center disabled:cursor-not-allowed"
    >
      <SendArrowIcon />
    </button>
  );
}

function SendArrowIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="19" x2="12" y2="5" />
      <polyline points="5 12 12 5 19 12" />
    </svg>
  );
}

const mdComponents: React.ComponentProps<typeof ReactMarkdown>["components"] = {
  h1: ({ children }) => (
    <h1 className="mt-4 mb-1.5 first:mt-0" style={{ fontSize: "1.2rem", fontWeight: 700, lineHeight: 1.3 }}>{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="mt-3 mb-1 first:mt-0" style={{ fontSize: "1.05rem", fontWeight: 700, lineHeight: 1.3 }}>{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="mt-2 mb-1 first:mt-0" style={{ fontSize: "0.95rem", fontWeight: 700, lineHeight: 1.3 }}>{children}</h3>
  ),
  p: ({ children }) => (
    <p className="mb-2 last:mb-0 leading-relaxed" style={{ fontWeight: 400 }}>{children}</p>
  ),
  ul: ({ children }) => (
    <ul className="list-disc list-outside pl-4 mb-2 space-y-0.5" style={{ fontWeight: 400 }}>{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="list-decimal list-outside pl-4 mb-2 space-y-0.5" style={{ fontWeight: 400 }}>{children}</ol>
  ),
  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
  strong: ({ children }) => <strong style={{ fontWeight: 700 }}>{children}</strong>,
  em: ({ children }) => <em className="italic">{children}</em>,
  code: ({ children }) => (
    <code
      style={{ background: "rgba(255,255,255,0.08)", color: "#e8e8e5", fontFamily: "var(--font-dm-mono), monospace" }}
      className="px-1.5 py-0.5 rounded text-xs"
    >
      {children}
    </code>
  ),
  blockquote: ({ children }) => (
    <blockquote
      style={{ borderColor: "rgba(255,255,255,0.15)", color: "#a0a09d" }}
      className="border-l-2 pl-3 italic my-2"
    >
      {children}
    </blockquote>
  ),
  table: ({ children }) => (
    <div className="overflow-x-auto my-3">
      <table style={{ borderCollapse: "collapse", width: "100%", fontSize: "0.9rem" }}>
        {children}
      </table>
    </div>
  ),
  thead: ({ children }) => (
    <thead style={{ borderBottom: "2px solid rgba(255,255,255,0.15)" }}>{children}</thead>
  ),
  tbody: ({ children }) => <tbody>{children}</tbody>,
  tr: ({ children }) => (
    <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.07)" }} className="transition-colors hover:bg-white/[0.03]">
      {children}
    </tr>
  ),
  th: ({ children }) => (
    <th
      style={{ color: "#c0c0bc", fontWeight: 600, textAlign: "left", padding: "0.5rem 0.75rem", fontFamily: "var(--font-quicksand), sans-serif" }}
    >
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td style={{ color: "#e8e8e5", padding: "0.45rem 0.75rem", verticalAlign: "top" }}>
      {children}
    </td>
  ),
};

function SourceItem({ source }: { source: SourceDoc }) {
  const [open, setOpen] = useState(false);
  const { title, content } = source;
  const body = content
    .split("\n")
    .filter((line) => !line.trim().match(/^#{1,3}\s+/))
    .join("\n")
    .trim();

  return (
    <div
      style={{ borderColor: "rgba(255,255,255,0.08)", borderRadius: "0.75rem" }}
      className="border overflow-hidden text-xs"
    >
      <button
        onClick={() => setOpen((v) => !v)}
        style={{ background: "rgba(255,255,255,0.04)", color: "#c0c0bc" }}
        className="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-white/[0.07] transition-colors"
      >
        <span style={{ color: "#6b6b68" }} className="shrink-0">{open ? "▾" : "▸"}</span>
        <span className="flex-1 font-medium truncate">{title}</span>
      </button>
      {open && (
        <pre
          style={{ background: "rgba(0,0,0,0.2)", color: "#a0a09d", borderTop: "1px solid rgba(255,255,255,0.06)", fontFamily: "var(--font-dm-mono), monospace" }}
          className="px-3 py-2.5 whitespace-pre-wrap leading-relaxed"
        >
          {body}
        </pre>
      )}
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex flex-col ${isUser ? "items-end" : "items-start"} gap-1`}>
      {isUser ? (
        <div
          style={{
            background: "#2e2e2b",
            color: "#e8e8e5",
            borderRadius: "1.125rem",
            borderBottomRightRadius: "0.25rem",
            maxWidth: "75%",
            fontSize: "1rem",
            lineHeight: "1.6",
            fontFamily: "var(--font-quicksand), sans-serif",
          }}
          className="px-4 py-2.5"
        >
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>
      ) : (
        <div className="w-full">
          <div
            style={{ color: "#e8e8e5", fontSize: "1rem", lineHeight: "1.7", fontFamily: "var(--font-source-serif), serif", fontWeight: 200 }}
            className="prose-sm max-w-none"
          >
            <ReactMarkdown components={mdComponents} remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
          </div>

          {message.sources && message.sources.length > 0 && (
            <div className="mt-3 space-y-1.5">
              <p style={{ color: "#6b6b68", fontSize: "0.75rem" }} className="px-0.5">
                {message.sources.length} source{message.sources.length !== 1 ? "s" : ""} retrieved
              </p>
              {message.sources.map((src, i) => (
                <SourceItem key={i} source={src} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}


function TypingIndicator() {
  return (
    <div className="flex items-start">
      <span className="flex gap-1 items-center py-1">
        <span
          style={{ background: "#6b6b68", animationDelay: "0ms" }}
          className="w-1.5 h-1.5 rounded-full animate-bounce"
        />
        <span
          style={{ background: "#6b6b68", animationDelay: "150ms" }}
          className="w-1.5 h-1.5 rounded-full animate-bounce"
        />
        <span
          style={{ background: "#6b6b68", animationDelay: "300ms" }}
          className="w-1.5 h-1.5 rounded-full animate-bounce"
        />
      </span>
    </div>
  );
}
