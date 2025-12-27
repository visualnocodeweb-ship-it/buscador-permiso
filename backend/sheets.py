import os
import gspread
from google.oauth2.service_account import Credentials
from unidecode import unidecode
from cachetools import TTLCache, cached
import json # Importar json para parsear la variable de entorno

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SHEET_NAMES = ["permisos", "discapacidad", "permiso-de-pesca-jubilados-65-2025-12-26", "malvinas"] # User provided sheet names

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

# Helper para normalizar headers/keys (minúsculas, sin acentos, sin caracteres especiales)
def _normalize_key(key):
    return unidecode(str(key).lower().replace(' ', '_').replace('.', '').replace('/', '').replace('(', '').replace(')', ''))

# Mapeo de claves normalizadas a claves estándar que espera el código
# Incluye variaciones comunes y los nombres de las columnas de PostgreSQL para consistencia
STANDARD_KEY_MAP = {
    _normalize_key('nombre'): 'nombre',
    _normalize_key('nombres'): 'nombre',
    _normalize_key('nombre_solo_nombre'): 'nombre',
    _normalize_key('apellido'): 'apellido',
    _normalize_key('apellidos'): 'apellido',
    _normalize_key('dni'): 'dni',
    _normalize_key('documento'): 'dni',
    _normalize_key('nro_documento'): 'dni', # De PostgreSQL
    _normalize_key('email'): 'email',
    _normalize_key('email_address'): 'email',
    _normalize_key('correo'): 'email',
    _normalize_key('celular'): 'celular',
    _normalize_key('cel'): 'celular',
    _normalize_key('telefono'): 'celular',
    _normalize_key('whatsapp'): 'celular',
    _normalize_key('customer_first_name'): 'nombre', # De PostgreSQL
    _normalize_key('customer_last_name'): 'apellido', # De PostgreSQL
    _normalize_key('customer_email'): 'email', # De PostgreSQL
    _normalize_key('customer_phone'): 'celular', # De PostgreSQL
    _normalize_key('nacimiento'): 'fecha_nacimiento',
    _normalize_key('fecha_de_nacimiento'): 'fecha_nacimiento',
    _normalize_key('region'): 'region',
    _normalize_key('region_pesca'): 'region', # De PostgreSQL
    _normalize_key('line_item_name'): 'permiso', # De PostgreSQL
    _normalize_key('status'): 'estado_permiso', # De PostgreSQL
    _normalize_key('fecha_inicio_permiso'): 'fecha_inicio_permiso',
    _normalize_key('fecha_de_creacion'): 'fecha_creacion', # De PostgreSQL
    _normalize_key('date_created'): 'fecha_creacion', # De PostgreSQL
}

def get_standardized_record(raw_record):
    standard_record = {}
    for raw_key, value in raw_record.items():
        normalized_key = _normalize_key(raw_key)
        target_key = STANDARD_KEY_MAP.get(normalized_key, raw_key) # Usa la clave original si no hay mapeo estándar
        standard_record[target_key] = value
    return standard_record


def get_sheets_client():
    try:
        creds = None
        # Opcion 1: Cargar desde un Secret File de Render (ruta estándar)
        secret_file_path = "/etc/secrets/credentials.json"
        if os.path.exists(secret_file_path):
            print(f"DEBUG: Cargando credenciales desde archivo secreto de Render: {secret_file_path}")
            creds = Credentials.from_service_account_file(secret_file_path, scopes=SCOPES)
        else:
            # Opcion 2: Cargar desde variable de entorno (para Render como fallback o si el archivo no se usa)
            google_credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
            # print(f"DEBUG: Valor de GOOGLE_CREDENTIALS_JSON (primeros 50 chars): {google_credentials_json[:50] if google_credentials_json else 'None'}") # Eliminado
            if google_credentials_json:
                print("DEBUG: Cargando credenciales desde variable de entorno GOOGLE_CREDENTIALS_JSON")
                creds_info = json.loads(google_credentials_json)
                creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
            else:
                # Opcion 3: Fallback a archivo local (para desarrollo)
                # La ruta es 'backend/credentials.json'
                print("DEBUG: Cargando credenciales desde archivo local backend/credentials.json")
                creds = Credentials.from_service_account_file("backend/credentials.json", scopes=SCOPES)

        if creds:
            client = gspread.authorize(creds)
            return client
        else:
            print("ERROR: No se pudieron encontrar credenciales para Google Sheets.")
            return None
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
            records = get_sheet_records_cached(worksheet)
            
            for record in records:
                # Normaliza el registro para acceder a las claves estandarizadas
                standard_record = get_standardized_record(record)

                nombre = unidecode(str(standard_record.get('nombre', '')).lower())
                apellido = unidecode(str(standard_record.get('apellido', '')).lower())
                dni = str(standard_record.get('dni', ''))

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
                    # Devuelve el registro estandarizado
                    standard_record['source'] = f"Google Sheets - {sheet_name}"
                    standard_record['estado_permiso'] = 'Permiso Pago' # Hardcode 'Permiso Pago' para Google Sheets
                    results.append(standard_record) # Añade el registro estandarizado
        except gspread.exceptions.WorksheetNotFound:
            print(f"Advertencia: Hoja '{sheet_name}' no encontrada en el Google Sheet.")
            continue
        except Exception as e:
            print(f"Error al buscar en la hoja '{sheet_name}': {e}")
            continue
    return results
