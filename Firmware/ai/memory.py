# persistent vector store using chromadb - tracks seen posts + semantic search
# dedup by post id so the same post never shows twice across reboots
# fix: chromadb 0.4.x dropped the old duckdb+parquet api, using PersistentClient now

import chromadb
from ai.embeddings import encode, encode_batch
from loguru import logger
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/chromadb")
os.makedirs(DB_PATH, exist_ok=True)

client     = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(
    name="nexus_ink_posts",
    metadata={"hnsw:space": "cosine"}
)

def store(post_id: str, text: str, metadata: dict = None):
    if is_seen(post_id):
        logger.info(f"post {post_id} already stored, skipping")
        return
    meta            = metadata or {}
    meta["post_id"] = post_id
    collection.add(
        documents  = [text],
        embeddings = [encode(text)],
        ids        = [post_id],
        metadatas  = [meta]
    )
    logger.success(f"stored {post_id}")

def store_batch(posts: list):
    new_posts = [p for p in posts if not is_seen(p["id"])]
    if not new_posts:
        logger.info("nothing new to store")
        return
    texts = [p["body"] for p in new_posts]
    collection.add(
        documents  = texts,
        embeddings = encode_batch(texts),
        ids        = [p["id"] for p in new_posts],
        metadatas  = [{"title": p["title"]} for p in new_posts]
    )
    logger.success(f"batch stored {len(new_posts)} posts")

def is_seen(post_id: str) -> bool:
    return len(collection.get(ids=[post_id])["ids"]) > 0

def query_similar(text: str, n: int = 3) -> list:
    results = collection.query(query_embeddings=[encode(text)], n_results=n)
    if not results["documents"] or not results["documents"][0]:
        return []
    return results["documents"][0]

def memory_size() -> int:
    return collection.count()

def clear_memory():
    logger.warning("wiping all memory")
    client.delete_collection("nexus_ink_posts")
    global collection
    collection = client.get_or_create_collection("nexus_ink_posts")
