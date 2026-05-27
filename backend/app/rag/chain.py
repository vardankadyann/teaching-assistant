from typing import Dict, List, Optional, Tuple

from openai import OpenAI

from app.config import settings
from app.models import SourceChunk, TeachingMode
from app.rag.store import COLLECTION_NAME, get_store

SYSTEM_PROMPTS = {
    TeachingMode.EXPLAIN: """You are a patient, encouraging teaching assistant. Use ONLY the provided course context to answer. If the context does not contain enough information, say so clearly and suggest what topic the student should review.

Guidelines:
- Explain concepts step by step at an appropriate level
- Use simple examples when helpful
- End with a brief check-for-understanding question when appropriate
- Cite which source excerpts you relied on (by filename)""",
    TeachingMode.SOCRATIC: """You are a Socratic tutor. Use ONLY the provided course context. Do NOT give the full answer immediately.

Guidelines:
- Ask guiding questions that help the student discover the answer
- Offer small hints drawn from the context when they are stuck
- Encourage reasoning and connect ideas across the material
- If the context is insufficient, say what is missing and ask a question that points them toward the right concept""",
    TeachingMode.QUIZ: """You are a quiz master tutor. Use ONLY the provided course context.

Guidelines:
- Generate 1-3 focused questions based on the student's request and the context
- After the student answers (in follow-up messages), give constructive feedback
- Explain why answers are correct or incorrect using the source material
- Increase difficulty gradually if the student is doing well""",
}


def build_context_block(chunks: List[dict]) -> str:
    if not chunks:
        return "(No course materials indexed yet.)"

    parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("source", "unknown")
        parts.append(f"[Excerpt {i} | {source}]\n{chunk['text']}")
    return "\n\n---\n\n".join(parts)


def chat(
    message: str,
    mode: TeachingMode,
    history: Optional[List[Dict[str, str]]] = None,
) -> Tuple[str, List[SourceChunk]]:
    store = get_store()
    retrieved = store.query(message)
    context = build_context_block(retrieved)

    if not settings.openai_api_key or settings.openai_api_key.startswith("sk-your"):
        return _fallback_response(message, retrieved, mode), [
            SourceChunk(**c) for c in retrieved
        ]

    try:
        client = OpenAI(api_key=settings.openai_api_key)
    except Exception:
        return _fallback_response(message, retrieved, mode), [
            SourceChunk(**c) for c in retrieved
        ]
    system = SYSTEM_PROMPTS[mode]
    system += f"\n\nCourse context:\n{context}"

    messages: List[Dict[str, str]] = [{"role": "system", "content": system}]
    for turn in (history or [])[-6:]:
        role = turn.get("role", "user")
        if role in ("user", "assistant"):
            messages.append({"role": role, "content": turn.get("content", "")})
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.4 if mode == TeachingMode.EXPLAIN else 0.6,
            max_tokens=1200,
        )
        answer = response.choices[0].message.content or ""
        return answer, [SourceChunk(**c) for c in retrieved]
    except Exception:
        return _fallback_response(message, retrieved, mode), [
            SourceChunk(**c) for c in retrieved
        ]


def _fallback_response(
    message: str, chunks: List[dict], mode: TeachingMode
) -> str:
    if not chunks:
        return (
            "No course materials are indexed yet. Upload PDF, TXT, or Markdown files, "
            "or click **Reload sample course**."
        )

    top = chunks[0]
    preview = top["text"][:500] + ("..." if len(top["text"]) > 500 else "")
    mode_note = {
        TeachingMode.EXPLAIN: "Here is the most relevant excerpt from your materials:",
        TeachingMode.SOCRATIC: "Consider this excerpt — what do you think it implies about your question?",
        TeachingMode.QUIZ: "Based on this excerpt, try answering your own question first:",
    }[mode]

    parts = [f"{mode_note}\n\n**Source:** {top['source']}\n\n{preview}"]
    if len(chunks) > 1:
        parts.append(f"\n\n_{len(chunks) - 1} more related excerpt(s) — expand Sources below._")
    return "".join(parts)
