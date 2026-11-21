import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from db import get_connection
import psycopg2.extras

conn = get_connection()
with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
    cur.execute('SELECT cod_recepcionista, nombres, apellidos, dni, usuario, password, rol, estado FROM public."Recepcionista" ORDER BY cod_recepcionista;')
    rows = cur.fetchall()

print(f"Total employees: {len(rows)}")
for r in rows:
    print(f"Code: {r['cod_recepcionista']} | Name: {r['nombres']} {r['apellidos']} | DNI: {r['dni']} | User: {r['usuario']} | Pass: {r['password']} | Rol: {r['rol']} | Estado: {r['estado']}")

conn.close()
