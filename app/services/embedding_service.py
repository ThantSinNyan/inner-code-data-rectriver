import pickle
import numpy as np
import faiss
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBED_MODEL = "text-embedding-3-small"


def embed_chunks(chunks: list[str]) -> np.ndarray:
    """Batch embed chunks (fast)."""
    resp = client.embeddings.create(model=EMBED_MODEL, input=chunks)
    embeddings = [d.embedding for d in resp.data]
    return np.array(embeddings, dtype=np.float32)


def save_embeddings(embeddings, chunks, file_path: str):
    with open(file_path, "wb") as f:
        pickle.dump((embeddings, chunks), f)


def load_embeddings(file_path: str):
    try:
        with open(file_path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None, None


def create_faiss_index(embeddings: np.ndarray):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index


def save_faiss_index(index, file_path: str):
    faiss.write_index(index, file_path)


def load_faiss_index(file_path: str):
    if os.path.exists(file_path):
        return faiss.read_index(file_path)
    return None


def search_index(index, query: str, top_k: int = 5) -> list[int]:
    """Search FAISS index using query embedding."""
    resp = client.embeddings.create(model=EMBED_MODEL, input=query)
    query_vec = np.array([resp.data[0].embedding], dtype=np.float32)
    distances, indices = index.search(query_vec, top_k)
    return indices[0]
