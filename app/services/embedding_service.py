import pickle
import numpy as np
import faiss
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBED_MODEL = "text-embedding-3-small"  # OpenAI embedding model


def embed_chunks(chunks: list[str]) -> np.ndarray:
    """Generate embeddings using OpenAI for a list of text chunks."""
    embeddings = []
    for chunk in chunks:
        resp = client.embeddings.create(model=EMBED_MODEL, input=chunk)
        embeddings.append(resp.data[0].embedding)
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


def search_index(index, query: str, top_k: int = 5) -> list[int]:
    """Search FAISS index using OpenAI embedding for the query."""
    resp = client.embeddings.create(model=EMBED_MODEL, input=query)
    query_vec = np.array([resp.data[0].embedding], dtype=np.float32)
    distances, indices = index.search(query_vec, top_k)
    return indices[0]
