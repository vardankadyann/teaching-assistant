const messagesEl = document.getElementById("messages");
const form = document.getElementById("form");
const input = document.getElementById("input");
const modeEl = document.getElementById("mode");
const statsEl = document.getElementById("stats");
const history = [];

async function loadStatus() {
  const res = await fetch("/api/status");
  const s = await res.json();
  statsEl.innerHTML = `<strong>${s.document_count}</strong> docs · <strong>${s.chunk_count}</strong> chunks` +
    (s.has_openai_key ? "" : "<br><small style='color:#fbbf24'>Set OPENAI_API_KEY for full answers</small>");
}

function addMsg(role, content, sources) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = content;
  if (sources?.length) {
    const det = document.createElement("details");
    det.className = "sources";
    det.innerHTML = `<summary>${sources.length} sources</summary>` +
      sources.map((s) => `<p><b>${s.source}</b> (${s.score != null ? Math.round(s.score * 100) + "%" : "—"})<br>${s.text.slice(0, 300)}…</p>`).join("");
    div.appendChild(det);
  }
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  addMsg("user", text);
  history.push({ role: "user", content: text });
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text, mode: modeEl.value, history }),
  });
  const data = await res.json();
  addMsg("assistant", data.answer, data.sources);
  history.push({ role: "assistant", content: data.answer });
});

document.getElementById("upload").onclick = () => document.getElementById("file").click();
document.getElementById("file").onchange = async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch("/api/ingest", { method: "POST", body: fd });
  const data = await res.json();
  addMsg("assistant", data.message);
  loadStatus();
  e.target.value = "";
};

document.getElementById("samples").onclick = async () => {
  const res = await fetch("/api/ingest/sample", { method: "POST" });
  addMsg("assistant", (await res.json()).message);
  loadStatus();
};

document.getElementById("clear").onclick = async () => {
  if (!confirm("Clear knowledge base?")) return;
  await fetch("/api/index", { method: "DELETE" });
  messagesEl.innerHTML = "";
  history.length = 0;
  loadStatus();
};

loadStatus();
