import os

# Configuración de conexión a PostgreSQL para Hotel Cumbre Real Airport
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "123"),
    "dbname": os.getenv("DB_NAME", "HOTEL_CUMBRE_REAL_AIRPORT")
}

# Configuración del servidor HTTP nativo
SERVER_CONFIG = {
    "host": os.getenv("SERVER_HOST", "0.0.0.0"),
    "port": int(os.getenv("SERVER_PORT", 8000))
}
