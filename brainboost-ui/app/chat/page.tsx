"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import "../globals.css"; // Note the path change since we are inside a folder
import ReactMarkdown from "react-markdown";
type Role = "human" | "ai";

interface ChatMessage {
  role: Role;
  content: string;
}

export default function ChatPage() {
  const router = useRouter();

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [fileName, setFileName] = useState("");
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isReady, setIsReady] = useState(false); // Prevents hydration mismatch

  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load data from sessionStorage on initial render
  useEffect(() => {
    const storedHistory = sessionStorage.getItem("chatHistory");
    const storedFileName = sessionStorage.getItem("fileName");

    if (!storedHistory || !storedFileName) {
      // If there's no data, kick them back to the upload page
      router.push("/");
    } else {
      setMessages(JSON.parse(storedHistory));
      setFileName(storedFileName);
      setIsReady(true);
    }
  }, [router]);

  // Scroll to bottom when messages update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    // 1. Optimistically show the user's message in the UI instantly
    const optimisticMessages: ChatMessage[] = [...messages, { role: "human", content: trimmed }];
    setMessages(optimisticMessages);
    setInput("");
    setLoading(true);

    try {
      // 2. Send ONLY the new question to the backend
      const response = await fetch("http://127.0.0.1:5000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: trimmed,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      // 3. Replace the entire frontend chat history with the backend's source of truth
      if (data.status === "success" && data.chat_history) {
        setMessages(data.chat_history);
        sessionStorage.setItem("chatHistory", JSON.stringify(data.chat_history));
      } else {
        throw new Error(data.error || "Failed to get history from server");
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        { role: "ai", content: "⚠️ Sorry, I ran into an error connecting to the server. Please try again." }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextareaInput = (e: React.FormEvent<HTMLTextAreaElement>) => {
    const el = e.currentTarget;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 140) + "px";
  };

  const handleReset = () => {
    sessionStorage.clear();
    router.push("/");
  };

  // Don't render until client-side data is loaded to prevent hydration errors
  if (!isReady) return null;

  const QUICK_PROMPTS = [
    "Explain this in simple words",
    "What are the key findings?",
    "What methods did they use?",
    "What does this mean for me?",
  ];

  return (
    <div className="chat-page">
      <aside className="sidebar">
        <div className="sidebar__logo">
          <span className="sidebar__logo-icon">📄</span>
          <span className="sidebar__logo-text">
            Paper<span>Pal</span>
          </span>
        </div>

        <div className="sidebar__paper-badge">
          <p className="sidebar__paper-label">Current Paper</p>
          <p className="sidebar__paper-name">{fileName}</p>
        </div>

        <p className="sidebar__section-title">Helpful prompts</p>
        {QUICK_PROMPTS.map((tip) => (
          <button key={tip} className="sidebar__chip" onClick={() => setInput(tip)}>
            {tip}
          </button>
        ))}

        <button className="sidebar__reset-btn" onClick={handleReset}>
          Upload new paper
        </button>
      </aside>

      <div className="chat-main">
        <header className="chat-topbar">
          <div>
            <p className="chat-topbar__title">Ask your paper anything</p>
            <p className="chat-topbar__sub">
              Responses are written in plain, easy to read language
            </p>
          </div>
          <div className="chat-topbar__status">
            <span className="chat-topbar__status-dot" />
            <span className="chat-topbar__status-label">Ready</span>
          </div>
        </header>

        <div className="chat-messages">
          <div className="chat-messages__inner">
            {messages.map((msg, i) => (
              <div key={i} className={`message-row message-row--${msg.role} `}>
                {msg.role === "ai" && (
                  <div className="message-avatar message-avatar--ai">🤖</div>
                )}
                <div className={`message-bubble message-bubble--${msg.role} markdown-body`}>
                  <ReactMarkdown >
                    {msg.content}
                  </ReactMarkdown>
                </div>
                {msg.role === "human" && (
                  <div className="message-avatar message-avatar--human">🧑</div>
                )}
              </div>
            ))}

            {loading && (
              <div className="message-row message-row--ai">
                <div className="message-avatar message-avatar--ai">🤖</div>
                <div className="loading-bubble">
                  <span className="loading-dot" />
                  <span className="loading-dot" />
                  <span className="loading-dot" />
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        </div>

        <div className="chat-inputbar">
          <div className="chat-inputbar__inner">
            <div className="chat-inputbar__box">
              <textarea

                ref={textareaRef}
                className="chat-inputbar__textarea"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                onInput={handleTextareaInput}
                placeholder="Ask a question about the paper…"
                rows={1}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || loading}
                className={`chat-inputbar__send-btn ${input.trim() && !loading
                  ? "chat-inputbar__send-btn--active"
                  : "chat-inputbar__send-btn--disabled"
                  }`}
              >
                {loading ? "⏳" : "➤"}
              </button>
            </div>
            <p className="chat-inputbar__hint">
              Press Enter to send · Shift+Enter for a new line
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}