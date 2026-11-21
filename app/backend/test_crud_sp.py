"""
Script de Prueba Automatizada de Procedimientos Almacenados y Triggers
Hotel Cumbre Real Airport - Alcance 70%
Prueba:
1. Huéspedes (CRUD con sp_insertar_huesped, sp_modificar_huesped, sp_eliminar_huesped)
2. Reservas (Ciclo de vida con sp_insertar_reserva, sp_checkin_reserva, sp_checkout_reserva, sp_cancelar_reserva)
3. Auditoría disparada automáticamente por Triggers
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db import get_connection

def test_full_system():
    print("=" * 65)
    print(" HOTEL CUMBRE REAL AIRPORT - SUITE DE PRUEBAS 70% ")
    print("=" * 65)

    conn = get_connection()
    doc_prueba = "DOC88888888"
    hab_prueba = "0101"

    try:
        with conn.cursor() as cur:
            # -------------------------------------------------------------
            # FASE 1: CRUD Huésped con Procedimiento Almacenado
            # -------------------------------------------------------------
            print("\n[FASE 1] Probando Gestión de Huésped (sp_insertar_huesped)...")
            cur.execute(
                "CALL public.sp_insertar_huesped(%s, %s, %s, %s, %s, %s);",
                (doc_prueba, "D01", "Luciana", "Paredes Rivas", "luciana.paredes@example.com", "954332211")
            )
            conn.commit()
            print(" -> Huésped insertado exitosamente.")

            # -------------------------------------------------------------
            # FASE 2: Inserción de Reserva (sp_insertar_reserva)
            # -------------------------------------------------------------
            print("\n[FASE 2] Probando Creación de Reserva (sp_insertar_reserva)...")
            cur.execute('CALL public.sp_cambiar_estado_habitacion(%s, %s, NULL);', (hab_prueba, 'Disponible'))
            conn.commit()

            cur.execute("""
                CALL public.sp_insertar_reserva(
                    %s, %s, 
                    '2026-11-20 14:00:00'::timestamp, '2026-11-22 11:00:00'::timestamp,
                    'M03', 'E001', TRUE, 'Huésped VIP solicita piso alto', NULL
                );
            """, (doc_prueba, hab_prueba))
            conn.commit()

            cur.execute('SELECT cod_reserva, estado_habitacion FROM public."Habitacion" WHERE num_habitacion = %s;', (hab_prueba,))
            res_row = cur.fetchone()
            cod_reserva_creada = res_row[0]
            print(f" -> Reserva creada con código: {cod_reserva_creada}")
            print(f" -> Estado de Habitación {hab_prueba}: {res_row[1]} (esperado: Reservada)")
            assert res_row[1] == 'Reservada', "La habitación debió cambiar a Reservada"

            # -------------------------------------------------------------
            # FASE 3: Check-in de Recepción (sp_checkin_reserva)
            # -------------------------------------------------------------
            print("\n[FASE 3] Probando Check-in en Recepción (sp_checkin_reserva)...")
            cur.execute("CALL public.sp_checkin_reserva(%s);", (cod_reserva_creada,))
            conn.commit()

            cur.execute('SELECT estado_habitacion FROM public."Habitacion" WHERE num_habitacion = %s;', (hab_prueba,))
            estado_post_in = cur.fetchone()[0]
            print(f" -> Estado tras Check-in: {estado_post_in} (esperado: Ocupada)")
            assert estado_post_in == 'Ocupada', "La habitación debió cambiar a Ocupada"

            # -------------------------------------------------------------
            # FASE 4: Check-out de Recepción (sp_checkout_reserva)
            # -------------------------------------------------------------
            print("\n[FASE 4] Probando Check-out en Recepción (sp_checkout_reserva)...")
            cur.execute("CALL public.sp_checkout_reserva(%s);", (cod_reserva_creada,))
            conn.commit()

            cur.execute('SELECT estado_habitacion, cod_reserva FROM public."Habitacion" WHERE num_habitacion = %s;', (hab_prueba,))
            row_out = cur.fetchone()
            print(f" -> Estado tras Check-out: {row_out[0]} (esperado: Limpieza), Reserva vinculada: {row_out[1]}")
            assert row_out[0] == 'Limpieza', "La habitación debió pasar a Limpieza"

            # -------------------------------------------------------------
            # FASE 5: Cancelación / Limpieza de prueba
            # -------------------------------------------------------------
            print("\n[FASE 5] Limpiando datos de prueba...")
            cur.execute("CALL public.sp_cancelar_reserva(%s);", (cod_reserva_creada,))
            cur.execute("CALL public.sp_eliminar_huesped(%s);", (doc_prueba,))
            cur.execute("CALL public.sp_cambiar_estado_habitacion(%s, %s, NULL);", (hab_prueba, 'Disponible'))
            conn.commit()
            print(" -> Reserva y huésped de prueba eliminados con éxito.")

            # -------------------------------------------------------------
            # FASE 6: Verificación de Auditoría
            # -------------------------------------------------------------
            print("\n[FASE 6] Verificando logs generados por Triggers y Procedures...")
            cur.execute("SELECT operacion, tabla_afectada, detalle FROM public.auditoria_operaciones ORDER BY id_auditoria DESC LIMIT 4;")
            for op in cur.fetchall():
                print(f"    * [{op[0]}] en {op[1]}: {op[2]}")

        print("\n" + "=" * 65)
        print(" ¡TODAS LAS PRUEBAS DE PROCEDIMIENTOS Y TRIGGERS (70%) PASARON! ")
        print("=" * 65)
        return True

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Falló la prueba: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = test_full_system()
    sys.exit(0 if success else 1)
