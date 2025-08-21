from fastapi import APIRouter, HTTPException
from app.models.plan_model import PlanRequest, PlanResponse
from app.services.pdf_service import extract_text_from_pdf, chunk_text
from app.services.embedding_service import (
    load_embeddings, save_embeddings, embed_chunks, create_faiss_index, search_index
)
from app.services.llm_service import query_llm
import os

router = APIRouter()

PDF_PATH = os.getenv("PDF_PATH", "app/document/Chiron_Healing_Map.pdf")
EMB_FILE = os.getenv("EMB_FILE", "app/vector_db/embeddings.pkl")


@router.post("/generate_plan", response_model=PlanResponse)
def generate_plan(request: PlanRequest):
    # Load or compute embeddings
    embeddings, chunks = load_embeddings(EMB_FILE)
    if embeddings is None:
        text = extract_text_from_pdf(PDF_PATH)
        chunks = chunk_text(text)
        embeddings = embed_chunks(chunks)
        save_embeddings(embeddings, chunks, EMB_FILE)

    # Build FAISS index
    index = create_faiss_index(embeddings)

    # Search
    indices = search_index(index, request.question)
    relevant_chunks = [chunks[i] for i in indices]

    # Query LLM
    context = "\n\n".join(relevant_chunks)
    plan_list = query_llm(context, request.sign, request.house)

    if not plan_list:
        raise HTTPException(status_code=500, detail="LLM could not generate a valid plan")

    return PlanResponse(
        sign=request.sign,
        house=request.house,
        plan=plan_list
    )

