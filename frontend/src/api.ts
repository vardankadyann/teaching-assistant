export type TeachingMode = "explain" | "socratic" | "quiz";

export interface SourceChunk {
  text: string;
  source: string;
  score: number | null;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: SourceChunk[];
  mode?: TeachingMode;
}

export interface Status {
  document_count: number;
  chunk_count: number;
  has_openai_key: boolean;
  collection_name: string;
}

export async function fetchStatus(): Promise<Status> {
  const res = await fetch("/api/status");
  if (!res.ok) throw new Error("Failed to load status");
  return res.json();
}

export async function sendChat(
  message: string,
  mode: TeachingMode,
  history: { role: string; content: string }[]
): Promise<{ answer: string; sources: SourceChunk[]; mode: TeachingMode }> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, mode, history }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Chat request failed");
  }
  return res.json();
}

export async function uploadDocument(file: File): Promise<{ chunks_added: number; message: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch("/api/ingest", { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export async function loadSampleMaterials(): Promise<{ message: string; total_chunks: number }> {
  const res = await fetch("/api/ingest/sample", { method: "POST" });
  if (!res.ok) throw new Error("Failed to load samples");
  return res.json();
}

export async function clearIndex(): Promise<void> {
  const res = await fetch("/api/index", { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to clear index");
}
