from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

import database, sheets
import os

# Clave de API para el panel de administración (en un caso real, usar variables de entorno)
ADMIN_API_KEY = "admin123"

app = FastAPI()

# Configuración de CORS para permitir la comunicación con el frontend
origins = [
    "http://localhost:5176",  # Puerto donde corre el frontend de Vite
    "http://127.0.0.1:5176",
    "https://buscador-permiso-frontend.onrender.com" # AÑADIDO: URL del frontend desplegado
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    email: str

class SearchResult(BaseModel):
    source: str
    data: Dict[str, Any]

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.get("/status")
def get_status():
    db_ok = database.test_db_connection()
    sheet_title = sheets.test_sheets_connection()

    return {
        "database_connection": "Exitosa" if db_ok else "Fallida",
        "google_sheets_connection": "Exitosa" if sheet_title else "Fallida",
        "spreadsheet_title": sheet_title if sheet_title else "No se pudo obtener"
    }

@app.post("/search", response_model=List[SearchResult])
async def search_data(request: SearchRequest):
    query = request.query.strip()
    email = request.email.strip()

    if not query:
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía.")
    if not email:
        raise HTTPException(status_code=400, detail="El email no puede estar vacío.")

    all_results: List[SearchResult] = []

    # Search in PostgreSQL
    db_results = database.search_by_name_dni(query)
    for res in db_results:
        all_results.append(SearchResult(source="PostgreSQL", data=res))

    # Search in Google Sheets
    sheets_results = sheets.search_sheets_by_name_dni(query)
    for res in sheets_results:
        all_results.append(SearchResult(source="Google Sheets", data=res))
    
    # Log the search query after getting results
    database.log_search_query(query, email, all_results)
    
    if not all_results:
        raise HTTPException(status_code=404, detail="No se encontraron resultados para la consulta.")

    return all_results

# --- Endpoints de Administración ---

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(x_api_key: str = Depends(api_key_header)):
    """Dependencia para verificar la clave de API en las cabeceras."""
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Clave de API no válida o ausente")

@app.get("/admin/stats", dependencies=[Depends(verify_api_key)])
async def get_admin_stats():
    """Devuelve estadísticas de la base de datos."""
    stats = database.get_stats()
    return stats

@app.get("/admin/history", dependencies=[Depends(verify_api_key)])
async def get_admin_history():
    """Devuelve el historial de búsquedas."""
    history = database.get_search_history()
    return history