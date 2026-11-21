import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from db import get_connection

conn = get_connection()
with conn.cursor() as cur:
    # Check if JeanPiero exists
    cur.execute("SELECT cod_recepcionista FROM public.\"Recepcionista\" WHERE LOWER(usuario) = 'jeanpiero';")
    exists = cur.fetchone()
    if not exists:
        cur.execute("""
            INSERT INTO public."Recepcionista" 
            (cod_recepcionista, nombres, apellidos, dni, usuario, password, rol, estado)
            VALUES ('E000', 'Jean Piero', 'Administrador', '10000000', 'JeanPiero', 'JeanPiero', 'Administrador', 'Activo')
            ON CONFLICT (cod_recepcionista) DO UPDATE 
            SET usuario = 'JeanPiero', password = 'JeanPiero', rol = 'Administrador', estado = 'Activo';
        """)
        print("Inserted JeanPiero as Administrator E000!")
    else:
        cur.execute("UPDATE public.\"Recepcionista\" SET password = 'JeanPiero', rol = 'Administrador', estado = 'Activo' WHERE LOWER(usuario) = 'jeanpiero';")
        print("Updated JeanPiero as Administrator!")

conn.commit()
conn.close()
