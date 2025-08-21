import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_chunks(chunks: list[str]) -> np.ndarray:
    return _model.encode(chunks, convert_to_numpy=True)


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
    query_vec = _model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_vec, top_k)
    return indices[0]
