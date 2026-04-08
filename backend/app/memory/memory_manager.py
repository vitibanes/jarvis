import json
from sqlmodel import select

from app.models.db_models import MemoryEntry
from app.utils.embeddings import cosine_similarity, simple_embed


class MemoryManager:
    def __init__(self, session):
        self.session = session

    def add(self, memory_type: str, content: str, task_id: int | None = None, key: str = "") -> MemoryEntry:
        emb = simple_embed(content)
        row = MemoryEntry(memory_type=memory_type, content=content, task_id=task_id, key=key, embedding_json=json.dumps(emb))
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def retrieve_relevant(self, query: str, limit: int = 5) -> list[MemoryEntry]:
        q = simple_embed(query)
        items = self.session.exec(select(MemoryEntry)).all()
        scored = []
        for item in items:
            emb = json.loads(item.embedding_json or "[]")
            scored.append((cosine_similarity(q, emb), item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [it for _, it in scored[:limit]]

    def rolling_summary(self, max_items: int = 20) -> str:
        items = self.session.exec(select(MemoryEntry).where(MemoryEntry.memory_type == "conversational").order_by(MemoryEntry.id.desc())).all()
        recent = list(reversed(items[:max_items]))
        text = "\n".join([m.content[:240] for m in recent])
        return text[-2000:]
