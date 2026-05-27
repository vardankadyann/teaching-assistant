import { useCallback, useEffect, useRef, useState } from "react";
import {
  ChatMessage,
  clearIndex,
  fetchStatus,
  loadSampleMaterials,
  sendChat,
  SourceChunk,
  Status,
  TeachingMode,
  uploadDocument,
} from "./api";

const MODES: { id: TeachingMode; label: string; hint: string }[] = [
  { id: "explain", label: "Explain", hint: "Clear step-by-step explanations" },
  { id: "socratic", label: "Socratic", hint: "Guiding questions, not direct answers" },
  { id: "quiz", label: "Quiz", hint: "Practice questions and feedback" },
];

const STARTERS = [
  "What is the difference between supervised and unsupervised learning?",
  "How do I know if my model is overfitting?",
  "Explain backpropagation in simple terms.",
];

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<TeachingMode>("explain");
  const [status, setStatus] = useState<Status | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedSource, setExpandedSource] = useState<number | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const refreshStatus = useCallback(async () => {
    try {
      setStatus(await fetchStatus());
    } catch {
      setStatus(null);
    }
  }, []);

  useEffect(() => {
    refreshStatus();
  }, [refreshStatus]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const historyForApi = messages.map((m) => ({
    role: m.role,
    content: m.content,
  }));

  async function handleSend(text?: string) {
    const msg = (text ?? input).trim();
    if (!msg || loading) return;

    setError(null);
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: msg, mode }]);
    setLoading(true);

    try {
      const res = await sendChat(msg, mode, historyForApi);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.answer,
          sources: res.sources,
          mode: res.mode,
        },
      ]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const res = await uploadDocument(file);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Added **${file.name}** to the knowledge base (${res.chunks_added} chunks indexed).`,
        },
      ]);
      await refreshStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  async function handleLoadSamples() {
    setUploading(true);
    setError(null);
    try {
      const res = await loadSampleMaterials();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.message },
      ]);
      await refreshStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load samples");
    } finally {
      setUploading(false);
    }
  }

  async function handleClear() {
    if (!confirm("Clear all indexed course materials?")) return;
    try {
      await clearIndex();
      setMessages([]);
      await refreshStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Clear failed");
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-icon">◈</span>
          <div>
            <h1>Teaching Assistant</h1>
            <p>RAG-powered tutor</p>
          </div>
        </div>

        <section className="panel">
          <h2>Teaching mode</h2>
          <div className="mode-grid">
            {MODES.map((m) => (
              <button
                key={m.id}
                type="button"
                className={`mode-btn ${mode === m.id ? "active" : ""}`}
                onClick={() => setMode(m.id)}
              >
                <span className="mode-label">{m.label}</span>
                <span className="mode-hint">{m.hint}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="panel">
          <h2>Knowledge base</h2>
          <div className="stats">
            <div>
              <span className="stat-value">{status?.document_count ?? "—"}</span>
              <span className="stat-label">Documents</span>
            </div>
            <div>
              <span className="stat-value">{status?.chunk_count ?? "—"}</span>
              <span className="stat-label">Chunks</span>
            </div>
          </div>
          {!status?.has_openai_key && (
            <p className="warn">
              No OpenAI key — retrieval works; set <code>OPENAI_API_KEY</code> in backend/.env for full answers.
            </p>
          )}
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.txt,.md"
            hidden
            onChange={handleUpload}
          />
          <button
            type="button"
            className="btn secondary"
            disabled={uploading}
            onClick={() => fileRef.current?.click()}
          >
            {uploading ? "Uploading…" : "Upload material"}
          </button>
          <button
            type="button"
            className="btn ghost"
            disabled={uploading}
            onClick={handleLoadSamples}
          >
            Reload sample course
          </button>
          <button type="button" className="btn danger ghost" onClick={handleClear}>
            Clear index
          </button>
        </section>

        <section className="panel starters">
          <h2>Try asking</h2>
          <ul>
            {STARTERS.map((q) => (
              <li key={q}>
                <button type="button" onClick={() => handleSend(q)}>
                  {q}
                </button>
              </li>
            ))}
          </ul>
        </section>
      </aside>

      <main className="chat">
        <div className="messages">
          {messages.length === 0 && (
            <div className="empty">
              <h2>Ask anything about your course</h2>
              <p>
                Answers are grounded in your uploaded materials. Sample ML notes load
                automatically on first start.
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <article
              key={i}
              className={`bubble ${msg.role}${msg.role === "assistant" ? " assistant" : ""}`}
            >
              {msg.role === "assistant" && msg.mode && (
                <span className="mode-tag">{msg.mode}</span>
              )}
              <div className="bubble-content">{formatContent(msg.content)}</div>
              {msg.sources && msg.sources.length > 0 && (
                <SourceList
                  sources={msg.sources}
                  expanded={expandedSource === i}
                  onToggle={() =>
                    setExpandedSource(expandedSource === i ? null : i)
                  }
                />
              )}
            </article>
          ))}

          {loading && (
            <article className="bubble assistant loading">
              <span className="dots">Thinking</span>
            </article>
          )}
          <div ref={bottomRef} />
        </div>

        {error && <div className="error-bar">{error}</div>}

        <form
          className="composer"
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
        >
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={`Ask in ${mode} mode…`}
            rows={2}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />
          <button type="submit" className="btn primary" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </main>
    </div>
  );
}

function formatContent(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return part.split("\n").map((line, j, arr) => (
      <span key={`${i}-${j}`}>
        {line}
        {j < arr.length - 1 && <br />}
      </span>
    ));
  });
}

function SourceList({
  sources,
  expanded,
  onToggle,
}: {
  sources: SourceChunk[];
  expanded: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="sources">
      <button type="button" className="sources-toggle" onClick={onToggle}>
        {expanded ? "Hide" : "Show"} {sources.length} source
        {sources.length !== 1 ? "s" : ""}
      </button>
      {expanded &&
        sources.map((s, i) => (
          <blockquote key={i} className="source-card">
            <header>
              <span>{s.source}</span>
              {s.score != null && (
                <span className="score">{(s.score * 100).toFixed(0)}% match</span>
              )}
            </header>
            <p>{s.text}</p>
          </blockquote>
        ))}
    </div>
  );
}
