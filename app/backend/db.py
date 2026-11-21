"""
Módulo de Acceso a Datos (PostgreSQL) - Sin Frameworks
Hotel Cumbre Real Airport
"""

import os
import sys
import time
import psycopg2
from psycopg2 import sql, extras

# Asegurar que el directorio backend esté en sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import DB_CONFIG

def get_connection(dbname=None):
    """
    Retorna una conexión activa a la base de datos PostgreSQL.
    Si se especifica dbname, se conecta a esa base de datos (ej. 'postgres' para tareas de administración).
    """
    config = DB_CONFIG.copy()
    if dbname:
        config["dbname"] = dbname
    return psycopg2.connect(**config)

def ensure_database_exists():
    """
    Verifica si la base de datos HOTEL_CUMBRE_REAL_AIRPORT existe.
    Si no existe, la crea una sola vez de forma permanente conectándose a 'postgres'.
    """
    target_db = DB_CONFIG["dbname"]
    conn = get_connection(dbname="postgres")
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (target_db,))
            exists = cur.fetchone() is not None
            if not exists:
                cur.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(target_db)))
                return True, f"Base de datos '{target_db}' creada exitosamente."
            else:
                return False, f"La base de datos '{target_db}' ya existe."
    finally:
        conn.close()

def check_connection_health():
    """
    Realiza una prueba completa de diagnóstico de conexión.
    Retorna un diccionario con estado, latencia, versión de PostgreSQL y conteo de tablas.
    """
    start_time = time.time()
    try:
        conn = get_connection()
        latency_ms = round((time.time() - start_time) * 1000, 2)
        with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute("SELECT version();")
            pg_version = cur.fetchone()["version"]
            
            cur.execute("""
                SELECT COUNT(*) as table_count 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
            """)
            table_count = cur.fetchone()["table_count"]

            # Obtener lista de tablas
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            tables = [row["table_name"] for row in cur.fetchall()]

        conn.close()
        return {
            "status": "connected",
            "database": DB_CONFIG["dbname"],
            "host": DB_CONFIG["host"],
            "port": DB_CONFIG["port"],
            "user": DB_CONFIG["user"],
            "latency_ms": latency_ms,
            "version": pg_version,
            "table_count": table_count,
            "tables": tables
        }
    except Exception as e:
        return {
            "status": "error",
            "database": DB_CONFIG["dbname"],
            "host": DB_CONFIG["host"],
            "port": DB_CONFIG["port"],
            "error": str(e)
        }
