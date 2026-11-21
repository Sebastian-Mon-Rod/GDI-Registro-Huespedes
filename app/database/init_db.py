"""
Script de Inicialización de la Base de Datos
Hotel Cumbre Real Airport
Ejecuta de forma secuencial y controlada:
1. schema.sql (Tablas, Secuencias, Índices)
2. seeds.sql (Datos semilla de prueba)
3. procedures_triggers.sql (Procedimientos almacenados y triggers)
"""

import os
import sys

# Permitir importar config y db desde backend
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from db import get_connection, ensure_database_exists, check_connection_health

def execute_sql_file(conn, filepath):
    print(f" -> Ejecutando {os.path.basename(filepath)}...")
    with open(filepath, "r", encoding="utf-8") as f:
        sql_content = f.read()
    
    with conn.cursor() as cur:
        cur.execute(sql_content)
    conn.commit()
    print(f"    [OK] {os.path.basename(filepath)} completado con éxito.")

def initialize_database():
    print("=" * 65)
    print(" HOTEL CUMBRE REAL AIRPORT - INICIALIZACIÓN DE BASE DE DATOS ")
    print("=" * 65)

    # 1. Asegurar que la base de datos exista
    created, msg = ensure_database_exists()
    print(f"\n[1/4] {msg}")

    # 2. Conectarse a HOTEL_CUMBRE_REAL_AIRPORT
    base_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(base_dir, "schema.sql")
    seeds_path = os.path.join(base_dir, "seeds.sql")
    sp_path = os.path.join(base_dir, "procedures_triggers.sql")

    conn = get_connection()
    try:
        print("\n[2/4] Creando estructura del modelo relacional en 3FN...")
        execute_sql_file(conn, schema_path)

        print("\n[3/4] Insertando 200 registros de prueba iniciales...")
        execute_sql_file(conn, seeds_path)

        print("\n[4/4] Instalando Procedimientos Almacenados y Triggers...")
        execute_sql_file(conn, sp_path)

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR CRÍTICO] Falló la inicialización: {e}")
        return False
    finally:
        conn.close()

    print("\n" + "=" * 65)
    print(" VERIFICACIÓN FINAL DEL ESTADO")
    print("=" * 65)
    health = check_connection_health()
    print(f" -> Tablas creadas: {health['table_count']}")
    print(f" -> Detalle de tablas: {', '.join(health['tables'])}")
    print(f" -> Latencia: {health['latency_ms']} ms")
    print(" -> ¡INICIALIZACIÓN COMPLETADA CON ÉXITO!")
    print("=" * 65)
    return True

if __name__ == "__main__":
    success = initialize_database()
    sys.exit(0 if success else 1)
