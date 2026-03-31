# turns text into 384-dim vectors w/ MiniLM so chromadb can do similarity search
# model loads once at import time so its not reloading every single call

from sentence_transformers import SentenceTransformer
from loguru import logger
import numpy as np

_model = SentenceTransformer("all-MiniLM-L6-v2")
logger.info("embedding model loaded")

def encode(text: str) -> list:
    if not text or not text.strip():
        return [0.0] * 384
    return _model.encode(text, normalize_embeddings=True).tolist()

def encode_batch(texts: list) -> list:
    if not texts:
        return []
    return [e.tolist() for e in _model.encode(texts, normalize_embeddings=True, batch_size=8)]

def cosine_similarity(a: list, b: list) -> float:
    a, b = np.array(a), np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
