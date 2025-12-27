import os
import psycopg2
from psycopg2.extras import RealDictCursor
# from dotenv import load_dotenv # REMOVIDO: No necesario en Render, puede causar conflictos
from datetime import datetime

# load_dotenv() # REMOVIDO: No necesario en Render, puede causar conflictos

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def test_db_connection():
    try:
        conn = get_db_connection()
        conn.close()
        return True
    except psycopg2.OperationalError as e:
        print(f"Error de conexión a la base de datos: {e}")
        return False

def search_by_name_dni(query: str):
    results = []
    clean_query = query.strip()
    if not clean_query:
        return results

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Habilitar la extensión unaccent si no existe
        cur.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")

        search_conditions = []
        params_list = []

        # Condición para buscar en nro_documento (siempre se incluye si hay query)
        search_conditions.append("nro_documento ILIKE %s") # ILIKE para insensible a mayúsculas/minúsculas
        params_list.append(f"%{clean_query}%")

        # Si la query no es puramente numérica (ej. "Pasaporte A123"), también buscar en nombres
        if not clean_query.isdigit():
            search_terms = clean_query.lower().split()
            name_sub_conditions = []
            for term in search_terms:
                name_sub_conditions.append("(unaccent(LOWER(customer_first_name)) ILIKE unaccent(%s) OR unaccent(LOWER(customer_last_name)) ILIKE unaccent(%s))")
                params_list.extend([f"%{term}%", f"%{term}%"])
            if name_sub_conditions:
                search_conditions.append(f"({' AND '.join(name_sub_conditions)})")

        if not search_conditions:
            return results # No debería ocurrir si clean_query no está vacío
        
        sql = f"SELECT * FROM orders WHERE {' OR '.join(search_conditions)} LIMIT 50;"
        params = tuple(params_list)

        cur.execute(sql, params)
        results = cur.fetchall()
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error inesperado en search_by_name_dni: {e}")
    return results

def log_search_query(query: str, email: str, results: list):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Ensure table exists (initial creation with all columns)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS historial_busquedas (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                email TEXT,
                query TEXT NOT NULL,
                results_count INTEGER,
                first_result_source TEXT,
                first_result_name TEXT
            );
        """)
        conn.commit() # Commit the CREATE TABLE if it happened

        # Add missing columns if they don't exist
        columns_to_add = {
            "email": "TEXT",
            "results_count": "INTEGER",
            "first_result_source": "TEXT",
            "first_result_name": "TEXT"
        }

        for col_name, col_type in columns_to_add.items():
            try:
                cur.execute(f"""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='historial_busquedas' AND column_name='{col_name}') THEN
                            ALTER TABLE historial_busquedas ADD COLUMN {col_name} {col_type};
                        END IF;
                    END
                    $$;
                """)
                conn.commit()
            except Exception as e:
                print(f"Advertencia: No se pudo añadir la columna '{col_name}' a 'historial_busquedas'. Puede que ya exista o haya otro error: {e}")
                conn.rollback() # Rollback if ALTER TABLE failed, but continue

        results_count = len(results)
        first_result_source = None
        first_result_name = None
        if results_count > 0:
            first_result = results[0]
            first_result_source = first_result.source
            # Utilizar 'nombre' y 'apellido' que ya vienen estandarizados
            first_result_name = f"{first_result.data.get('nombre', '')} {first_result.data.get('apellido', '')}".strip()

        cur.execute(
            """
            INSERT INTO historial_busquedas (email, query, results_count, first_result_source, first_result_name) 
            VALUES (%s, %s, %s, %s, %s);
            """, 
            (email, query, results_count, first_result_source, first_result_name)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error inesperado en log_search_query: {e}")
        return False

def get_search_history(limit: int = 100):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM historial_busquedas ORDER BY timestamp DESC LIMIT %s;", (limit,))
        history = cur.fetchall()
        cur.close()
        conn.close()
        return history
    except Exception as e:
        print(f"Error al obtener el historial de búsquedas: {e}")
        return []

def get_stats():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Contar consultas
        cur.execute("SELECT COUNT(*) FROM historial_busquedas;")
        query_count = cur.fetchone()[0]
        
        # Contar registros en 'orders'
        cur.execute("SELECT COUNT(*) FROM orders;")
        record_count = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return {"query_count": query_count, "record_count": record_count}
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        return {"query_count": 0, "record_count": 0}
