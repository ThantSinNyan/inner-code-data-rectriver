from fastapi import APIRouter, HTTPException
from app.models.plan_model import PlanRequest, PlanResponse
from app.models.overview_model import OverviewResponse
from app.services.pdf_service import extract_text_from_pdf, chunk_text
from app.services.embedding_service import (
    load_embeddings, save_embeddings, embed_chunks,
    create_faiss_index, save_faiss_index, load_faiss_index, search_index
)
from app.services.healing_service import generate_healing_plan
from app.services.overview_service import generate_overview
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
        chunks = chunk_text(text, max_len=200)
        embeddings = embed_chunks(chunks)
        save_embeddings(embeddings, chunks, EMB_FILE)

        index = create_faiss_index(embeddings)
        save_faiss_index(index, INDEX_FILE)

    return embeddings, chunks, index


@router.post("/generate_plan", response_model=PlanResponse)
def generate_plan(request: PlanRequest):
    embeddings, chunks, index = _prepare_index()

    indices = search_index(index, request.question, top_k=3)
    relevant_chunks = [chunks[i] for i in indices]
    context = "\n\n".join(relevant_chunks)

    plan_list = generate_healing_plan(context, request.sign, request.house)

    if not plan_list:
        raise HTTPException(status_code=500, detail="LLM could not generate a valid plan")

    return PlanResponse(
        sign=request.sign,
        house=request.house,
        plan=plan_list
    )


@router.post("/generate_overview", response_model=OverviewResponse)
def generate_overview_route(request: PlanRequest):
    embeddings, chunks, index = _prepare_index()

    indices = search_index(index, request.question, top_k=3)
    relevant_chunks = [chunks[i] for i in indices]
    context = "\n\n".join(relevant_chunks)

    overview = generate_overview(context, request.sign, request.house)

    if not overview:
        raise HTTPException(status_code=500, detail="LLM could not generate a valid overview")

    return OverviewResponse(
        sign=request.sign,
        house=request.house,
        **overview
    )
