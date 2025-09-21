from fastapi import APIRouter, HTTPException
from app.models.plan_model import PlanRequest, PlanResponse, PlanEndUserRequest
from app.models.overview_model import OverviewResponse
from app.services.pdf_service import extract_text_from_pdf, chunk_text
from app.services.embedding_service import (
    load_embeddings, save_embeddings, embed_chunks,
    create_faiss_index, save_faiss_index, load_faiss_index, search_index
)
from app.services.healing_service import generate_healing_plan
from app.services.overview_service import generate_overview
from app.services.sign_house_convector import calculate_chiron_position
from app.services.location_convector import get_lat_lon_timezone

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
    questionForSign="Chiron in "+request.sign+ "House, Life Area Focus Extra Daily, Prompt, meditation"
    questionForHouse=request.house +"House, Life Area Focus Extra Daily, Prompt, meditation"
    indicesSign = search_index(index, questionForSign, top_k=2)
    indicesHouse = search_index(index, questionForHouse, top_k=2)
    relevant_chunks_sign = [chunks[i] for i in indicesSign]
    relevant_chunks_house = [chunks[i] for i in indicesHouse]
    context = "\n\n".join(relevant_chunks_sign + relevant_chunks_house)

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
    questionForSign="Chiron in "+request.sign+ "House, Life Area Focus Extra Daily, Prompt, meditation"
    questionForHouse=request.house +"House, Life Area Focus Extra Daily, Prompt, meditation"
    indicesSign = search_index(index, questionForSign, top_k=2)
    indicesHouse = search_index(index, questionForHouse, top_k=2)
    relevant_chunks_sign = [chunks[i] for i in indicesSign]
    relevant_chunks_house = [chunks[i] for i in indicesHouse]
    context = "\n\n".join(relevant_chunks_sign + relevant_chunks_house)

    overview = generate_overview(context, request.sign, request.house, request.language)

    if not overview:
        raise HTTPException(status_code=500, detail="LLM could not generate a valid overview")

    return OverviewResponse(
        sign=request.sign,
        house=request.house,
        **overview
    )

@router.post("/generate_overview_end_user", response_model=OverviewResponse)
def generate_overview_route(request: PlanEndUserRequest):
    # Step 1: Convert birthPlace → city, country, lat/lon, timezone
    if ',' in request.birthPlace:
        city_input, country_input = [x.strip() for x in request.birthPlace.split(',', 1)]
    else:
        city_input = request.birthPlace.strip()
        country_input = ""  # Let service fuzzy match country if possible

    loc_info = get_lat_lon_timezone(country_input, city_input)
    if not loc_info:
        raise HTTPException(status_code=400, detail="Could not resolve birthPlace to a valid location")

    # Step 2: Calculate Chiron → sign and house
    chiron_info = calculate_chiron_position(
        birth_date=request.birthDate,
        birth_time=request.birthTime,
        timezone=loc_info["timezone_offset"],
        latitude=loc_info["latitude"],
        longitude=loc_info["longitude"]
    )

    sign = chiron_info["zodiac_sign"]
    chiron_house = chiron_info["house"]
    house=ordinal(chiron_house)

    # Step 3: Prepare context and call generate_overview
    embeddings, chunks, index = _prepare_index()
    indices = search_index(index, request.language, top_k=3) 
    relevant_chunks = [chunks[i] for i in indices]
    context = "\n\n".join(relevant_chunks)

    overview = generate_overview(context, sign, house)
    if not overview:
        raise HTTPException(status_code=500, detail="LLM could not generate a valid overview")

    # Step 4: Return response
    return OverviewResponse(
        sign=sign,
        house=house,
        **overview
    )
def ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:  # handles 11th, 12th, 13th, etc.
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"