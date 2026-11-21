"""
Script de Actualización de Base de Datos - Módulo de Empleados y Autenticación RBAC
Hotel Cumbre Real Airport / AlojaGest
Agrega soporte para:
1. Columnas de credenciales (DNI, Usuario, Contraseña y Rol: Administrador / Recepcionista).
2. Procedimientos almacenados para CRUD de empleados:
   - sp_insertar_recepcionista
   - sp_modificar_recepcionista
   - sp_eliminar_recepcionista
3. Inicialización del Administrador Principal (E001: Ana Torres / admin / DNI: 10000001)
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from db import get_connection

def upgrade_schema():
    print("=" * 65)
    print(" ACTUALIZANDO ESQUEMA DE EMPLEADOS Y ROLES (ALOJAGEST) ")
    print("=" * 65)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Agregar columnas a Recepcionista si no existen
            cur.execute("""
                ALTER TABLE public."Recepcionista" 
                ADD COLUMN IF NOT EXISTS dni VARCHAR(20) DEFAULT '12345678',
                ADD COLUMN IF NOT EXISTS usuario VARCHAR(50),
                ADD COLUMN IF NOT EXISTS password VARCHAR(100) DEFAULT '12345678',
                ADD COLUMN IF NOT EXISTS rol VARCHAR(20) DEFAULT 'Recepcionista',
                ADD COLUMN IF NOT EXISTS estado VARCHAR(15) DEFAULT 'Activo';
            """)

            # 2. Asignar usuarios y DNIs predeterminados a los 20 recepcionistas
            cur.execute('SELECT cod_recepcionista, nombres, apellidos FROM public."Recepcionista";')
            empleados = cur.fetchall()

            for emp in empleados:
                cod, nombres, apellidos = emp
                # Generar usuario amigable (ej: ana.torres) y dni correlativo
                num_parte = cod.replace('E', '')
                dni_calc = f"7000{num_parte.zfill(4)}"
                primer_nombre = nombres.split()[0].lower()
                primer_apellido = apellidos.split()[0].lower()
                user_calc = f"{primer_nombre}.{primer_apellido}"
                
                # E001 es el Administrador principal
                if cod == 'E001':
                    cur.execute("""
                        UPDATE public."Recepcionista"
                        SET dni = '10000001',
                            usuario = 'admin',
                            password = 'admin',
                            rol = 'Administrador'
                        WHERE cod_recepcionista = 'E001';
                    """)
                else:
                    cur.execute("""
                        UPDATE public."Recepcionista"
                        SET dni = %s,
                            usuario = %s,
                            password = %s,
                            rol = 'Recepcionista'
                        WHERE cod_recepcionista = %s AND (usuario IS NULL OR usuario = '');
                    """, (dni_calc, user_calc, dni_calc, cod))

            # 3. Procedimiento para insertar empleado
            cur.execute("""
                CREATE OR REPLACE PROCEDURE public.sp_insertar_recepcionista(
                    IN p_nombres VARCHAR(255),
                    IN p_apellidos VARCHAR(255),
                    IN p_dni VARCHAR(20),
                    IN p_usuario VARCHAR(50),
                    IN p_password VARCHAR(100),
                    IN p_rol VARCHAR(20),
                    INOUT p_cod VARCHAR(4) DEFAULT NULL
                )
                LANGUAGE plpgsql
                AS $$
                DECLARE
                    v_cod VARCHAR(4);
                BEGIN
                    IF p_nombres IS NULL OR TRIM(p_nombres) = '' OR p_apellidos IS NULL OR TRIM(p_apellidos) = '' THEN
                        RAISE EXCEPTION 'Nombres y apellidos son requeridos.';
                    END IF;

                    IF p_dni IS NULL OR TRIM(p_dni) = '' THEN
                        RAISE EXCEPTION 'El DNI del empleado es obligatorio.';
                    END IF;

                    v_cod := 'E' || LPAD(NEXTVAL('public.recepcionista_codigo_seq')::TEXT, 3, '0');
                    p_cod := v_cod;

                    INSERT INTO public."Recepcionista" (cod_recepcionista, nombres, apellidos, dni, usuario, password, rol, estado)
                    VALUES (
                        v_cod, 
                        p_nombres, 
                        p_apellidos, 
                        p_dni, 
                        COALESCE(p_usuario, v_cod), 
                        COALESCE(p_password, p_dni), 
                        COALESCE(p_rol, 'Recepcionista'),
                        'Activo'
                    );

                    INSERT INTO public.auditoria_operaciones(tabla_afectada, operacion, registro_id, detalle)
                    VALUES ('Recepcionista', 'INSERT', v_cod, 'Nuevo empleado registrado: ' || p_nombres || ' ' || p_apellidos || ' (Rol: ' || p_rol || ')');
                END;
                $$;
            """)

            # 4. Procedimiento para modificar empleado
            cur.execute("""
                CREATE OR REPLACE PROCEDURE public.sp_modificar_recepcionista(
                    IN p_cod VARCHAR(4),
                    IN p_nombres VARCHAR(255),
                    IN p_apellidos VARCHAR(255),
                    IN p_dni VARCHAR(20),
                    IN p_usuario VARCHAR(50),
                    IN p_password VARCHAR(100),
                    IN p_rol VARCHAR(20),
                    IN p_estado VARCHAR(15)
                )
                LANGUAGE plpgsql
                AS $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM public."Recepcionista" WHERE cod_recepcionista = p_cod) THEN
                        RAISE EXCEPTION 'El empleado con código % no existe.', p_cod;
                    END IF;

                    UPDATE public."Recepcionista"
                    SET nombres = p_nombres,
                        apellidos = p_apellidos,
                        dni = p_dni,
                        usuario = p_usuario,
                        password = COALESCE(NULLIF(p_password, ''), password),
                        rol = p_rol,
                        estado = COALESCE(p_estado, estado)
                    WHERE cod_recepcionista = p_cod;

                    INSERT INTO public.auditoria_operaciones(tabla_afectada, operacion, registro_id, detalle)
                    VALUES ('Recepcionista', 'UPDATE', p_cod, 'Actualización de datos del empleado: ' || p_nombres || ' ' || p_apellidos);
                END;
                $$;
            """)

            # 5. Procedimiento para dar de baja / eliminar empleado
            cur.execute("""
                CREATE OR REPLACE PROCEDURE public.sp_eliminar_recepcionista(
                    IN p_cod VARCHAR(4)
                )
                LANGUAGE plpgsql
                AS $$
                BEGIN
                    IF p_cod = 'E001' THEN
                        RAISE EXCEPTION 'No se puede eliminar al Administrador principal del sistema.';
                    END IF;

                    -- Cambiar estado a Inactivo para preservar integridad referencial de reservas/pagos pasados
                    UPDATE public."Recepcionista"
                    SET estado = 'Inactivo'
                    WHERE cod_recepcionista = p_cod;

                    INSERT INTO public.auditoria_operaciones(tabla_afectada, operacion, registro_id, detalle)
                    VALUES ('Recepcionista', 'DELETE', p_cod, 'Empleado desactivado/dado de baja');
                END;
                $$;
            """)

        conn.commit()
        print(" [OK] Columnas añadidas y Procedimientos Almacenados de Empleados instalados exitosamente.")
        return True
    except Exception as e:
        conn.rollback()
        print(f" [ERROR] Error durante la actualización: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = upgrade_schema()
    sys.exit(0 if success else 1)
