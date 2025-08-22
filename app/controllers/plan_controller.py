from fastapi import APIRouter, HTTPException
from app.models.plan_model import PlanRequest, PlanResponse
from app.services.pdf_service import extract_text_from_pdf, chunk_text
from app.services.embedding_service import (
    load_embeddings, save_embeddings, embed_chunks,
    create_faiss_index, save_faiss_index, load_faiss_index, search_index
)
from app.services.llm_service import query_llm
import os

router = APIRouter()

PDF_PATH = os.getenv("PDF_PATH", "app/document/Chiron_Healing_Map.pdf")
EMB_FILE = os.getenv("EMB_FILE", "app/vector_db/embeddings.pkl")
INDEX_FILE = os.getenv("INDEX_FILE", "app/vector_db/faiss.index")


def _prepare_index():
    embeddings, chunks = load_embeddings(EMB_FILE)
    index = load_faiss_index(INDEX_FILE)

    if embeddings is None or index is None:
        # First-time load
        text = extract_text_from_pdf(PDF_PATH)
        chunks = chunk_text(text, max_len=200)  # smaller chunks → faster context
        embeddings = embed_chunks(chunks)
        save_embeddings(embeddings, chunks, EMB_FILE)

        index = create_faiss_index(embeddings)
        save_faiss_index(index, INDEX_FILE)

    return embeddings, chunks, index


@router.post("/generate_plan", response_model=PlanResponse)
def generate_plan(request: PlanRequest):
    embeddings, chunks, index = _prepare_index()

    # Search with fewer chunks for speed
    indices = search_index(index, request.question, top_k=3)
    relevant_chunks = [chunks[i] for i in indices]

    context = "\n\n".join(relevant_chunks)
    plan_list = query_llm(context, request.sign, request.house)

    if not plan_list:
        raise HTTPException(status_code=500, detail="LLM could not generate a valid plan")

    return PlanResponse(
        sign=request.sign,
        house=request.house,
        plan=plan_list
    )

