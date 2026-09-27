"""
Local embedding generation using sentence-transformers.

- Model: all-MiniLM-L6-v2 (384 dims, ~90MB, runs on CPU)
- No API key, no quota, no network calls after first load.
- Lazy-loads the model on first use so importing the module is cheap.
- In-memory cache prevents re-embedding the same text twice in a process.
"""

import math
from typing import List, Dict

MODEL_NAME = "all-MiniLM-L6-v2"

_model = None
_EMBED_CACHE: Dict[str, List[float]] = {}


def _get_model():
    """Lazy-load the sentence-transformers model on first use."""
    global _model
    if _model is None:
        print(f"[embeddings] loading {MODEL_NAME} (first call only)...")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
        print("[embeddings] model ready")
    return _model


def embed(text: str) -> List[float]:
    """
    Return the embedding vector for a single string.
    Cached in memory. Uses the local MiniLM model.
    """
    if not text:
        return []

    cache_key = text.strip().lower()
    if cache_key in _EMBED_CACHE:
        return _EMBED_CACHE[cache_key]

    model = _get_model()
    vec = model.encode(text, convert_to_numpy=True).tolist()
    _EMBED_CACHE[cache_key] = vec
    return vec


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two vectors. Returns 0.0 on dimension mismatch or empty."""
    if not a or not b:
        return 0.0

    if len(a) != len(b):
        print(f"[embeddings] dimension mismatch: {len(a)} vs {len(b)}")
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)
