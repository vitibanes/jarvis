import math
import re
from collections import Counter


def simple_embed(text: str) -> list[float]:
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    counts = Counter(tokens)
    if not counts:
        return [0.0]
    norm = math.sqrt(sum(v * v for v in counts.values()))
    # lightweight deterministic embedding alternative for MVP
    return [sum((hash(t) % 1000) * c for t, c in counts.items()) / (1000 * norm)]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    size = min(len(a), len(b))
    dot = sum(a[i] * b[i] for i in range(size))
    na = math.sqrt(sum(x * x for x in a[:size]))
    nb = math.sqrt(sum(x * x for x in b[:size]))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
