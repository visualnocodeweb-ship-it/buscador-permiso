import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from unidecode import unidecode
from cachetools import TTLCache, cached
import json # Importar json para parsear la variable de entorno

load_dotenv()

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
# CREDENTIALS_FILE = "credentials.json" # Ya no se usa directamente
SHEET_NAMES = ["permisos", "discapacidad", "permiso-de-pesca-jubilados-65-2025-12-26", "malvinas"] # User provided sheet names

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

def get_sheets_client():
    try:
        # Intentar cargar credenciales desde variable de entorno (para Render)
        google_credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if google_credentials_json:
            creds_info = json.loads(google_credentials_json)
            creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        else:
            # Fallback a archivo local (para desarrollo)
            creds = Credentials.from_service_account_file("backend/credentials.json", scopes=SCOPES) # Ruta corregida

        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"Error de autenticación con Google: {e}")
        return None

def test_sheets_connection():
    client = get_sheets_client()
    if client:
        try:
            spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
            return spreadsheet.title
        except gspread.exceptions.SpreadsheetNotFound:
            print("Error: No se encontró la hoja de cálculo. Revisa el GOOGLE_SHEET_ID y los permisos.")
            return None
        except Exception as e:
            print(f"Error al abrir la hoja de cálculo: {e}")
            return None
    return None

# Cache para los registros de las hojas de Google, con un TTL (Time To Live) de 10 minutos
# Esto significa que los datos se mantendrán en memoria durante 10 minutos antes de volver a ser pedidos a Google.
cache = TTLCache(maxsize=10, ttl=600)

@cached(cache)
def get_sheet_records_cached(worksheet):
    """
    Obtiene todos los registros de una worksheet y los cachea.
    La clave del caché será el objeto 'worksheet' en sí mismo.
    """
    print(f"CACHE MISS: Obteniendo registros para la hoja '{worksheet.title}' desde Google Sheets.")
    return worksheet.get_all_records()

def search_sheets_by_name_dni(query: str):
    results = []
    clean_query = unidecode(query.strip().lower())
    if not clean_query:
        return results
        
    client = get_sheets_client()
    if not client:
        return results

    try:
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
    except Exception as e:
        print(f"Error al abrir la hoja de cálculo para buscar: {e}")
        return results

    for sheet_name in SHEET_NAMES:
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            # Usamos la función cacheada en lugar de la llamada directa
            records = get_sheet_records_cached(worksheet)
            
            for record in records:
                # Asumiendo los nombres de las columnas. ¡¡¡IMPORTANTE: AJUSTAR SI SON DIFERENTES!!!
                nombre = unidecode(str(record.get('nombre', '')).lower())
                apellido = unidecode(str(record.get('apellido', '')).lower())
                dni = str(record.get('dni', ''))

                match_found = False
                if clean_query.isdigit():
                    if clean_query in dni:
                        match_found = True
                else:
                    search_terms = clean_query.split()
                    full_name = f"{nombre} {apellido}"
                    if all(term in full_name for term in search_terms):
                        match_found = True

                if match_found:
                    record['source'] = f"Google Sheets - {sheet_name}"
                    results.append(record)
        except gspread.exceptions.WorksheetNotFound:
            print(f"Advertencia: Hoja '{sheet_name}' no encontrada en el Google Sheet.")
            continue
        except Exception as e:
            print(f"Error al buscar en la hoja '{sheet_name}': {e}")
            continue
    return results
