"""
Script de Prueba de Conexión y Diagnóstico de PostgreSQL
Hotel Cumbre Real Airport
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db import ensure_database_exists, check_connection_health

def run_test():
    print("=" * 60)
    print(" HOTEL CUMBRE REAL AIRPORT - PRUEBA DE CONEXIÓN A POSTGRESQL ")
    print("=" * 60)
    
    # 1. Asegurar existencia de la base de datos
    print("\n[Paso 1] Verificando base de datos...")
    try:
        created, msg = ensure_database_exists()
        print(f" -> {msg}")
    except Exception as e:
        print(f" [ERROR] No se pudo verificar o crear la base de datos: {e}")
        return False

    # 2. Probar conexión y obtener diagnóstico
    print("\n[Paso 2] Ejecutando diagnóstico de conexión...")
    health = check_connection_health()
    
    if health["status"] == "connected":
        print(" -> ¡CONEXIÓN EXITOSA!")
        print(f" -> Servidor: {health['host']}:{health['port']}")
        print(f" -> Usuario: {health['user']}")
        print(f" -> Base de datos: {health['database']}")
        print(f" -> Latencia de ping: {health['latency_ms']} ms")
        print(f" -> Versión: {health['version'].split(',')[0]}")
        print(f" -> Total de tablas encontradas: {health['table_count']}")
        if health['tables']:
            print(f" -> Tablas actuales: {', '.join(health['tables'])}")
        else:
            print(" -> Nota: La base de datos aún no tiene tablas (pendiente ejecutar schema.sql).")
        print("\n" + "=" * 60)
        print(" DIAGNÓSTICO: OPERATIVO Y LISTO PARA LA SEMANA 1")
        print("=" * 60)
        return True
    else:
        print(" [FALLO DE CONEXIÓN]")
        print(f" -> Error detectado: {health.get('error')}")
        print("\n" + "=" * 60)
        print(" DIAGNÓSTICO: ERROR DE ACCESO")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
