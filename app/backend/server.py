"""
=============================================================================
 ALOJAGEST - SISTEMA INTEGRAL DE GESTIÓN HOTELERA
 Servidor de Aplicación Multihilo Nativo (Python Puro) - Cero Dependencias
 Compatible con PostgreSQL 14+ / 18+
=============================================================================
"""

import os
import sys
import json
import mimetypes
from datetime import datetime, date, time as dt_time
from decimal import Decimal
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs

# Importar configuración y conexión a PostgreSQL
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import SERVER_CONFIG
from db import get_connection, check_connection_health
import psycopg2.extras

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Servidor HTTP multihilo nativo para manejar peticiones concurrentes sin bloqueos"""
    daemon_threads = True

class CustomJSONEncoder(json.JSONEncoder):
    """Codificador JSON robusto para serializar tipos de PostgreSQL (Decimal, date, datetime, time)"""
    def default(self, obj):
        if isinstance(obj, (datetime, date, dt_time)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

class AlojaGestHandler(BaseHTTPRequestHandler):
    """
    Controlador HTTP principal de AlojaGest.
    Maneja autenticación, roles (Admin/Recepcionista), CRUD mediante Stored Procedures,
    Centro de Reportes y servidor de archivos estáticos.
    """

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def _read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            raw_data = self.rfile.read(content_length).decode("utf-8")
            return json.loads(raw_data)
        return {}

    def _send_json(self, data, status=200):
        self._set_headers(status, "application/json")
        encoded = json.dumps(data, ensure_ascii=False, cls=CustomJSONEncoder).encode("utf-8")
        self.wfile.write(encoded)

    def _send_error(self, message, status=400):
        self._set_headers(status, "application/json")
        encoded = json.dumps({"success": False, "error": str(message)}, ensure_ascii=False).encode("utf-8")
        self.wfile.write(encoded)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # 1. API: Diagnóstico de Conexión
        if path == "/api/health":
            health = check_connection_health()
            self._send_json({"success": health["status"] == "connected", "data": health})
            return

        # 2. API: Estadísticas Ejecutivas del Dashboard
        if path == "/api/dashboard":
            try:
                conn = get_connection()
                with conn.cursor() as cur:
                    cur.execute('SELECT COUNT(*) FROM public."Huesped";')
                    total_huespedes = cur.fetchone()[0]

                    cur.execute('SELECT COUNT(*) FROM public."Reserva";')
                    total_reservas = cur.fetchone()[0]

                    cur.execute('SELECT COUNT(*) FROM public."Habitacion";')
                    total_habitaciones = cur.fetchone()[0]

                    cur.execute("SELECT COUNT(*) FROM public.\"Habitacion\" WHERE estado_habitacion = 'Disponible';")
                    hab_disponibles = cur.fetchone()[0]

                    cur.execute("SELECT COUNT(*) FROM public.\"Habitacion\" WHERE estado_habitacion = 'Reservada';")
                    hab_reservadas = cur.fetchone()[0]

                    cur.execute("SELECT COUNT(*) FROM public.\"Habitacion\" WHERE estado_habitacion = 'Ocupada';")
                    hab_ocupadas = cur.fetchone()[0]

                    cur.execute("SELECT COUNT(*) FROM public.\"Habitacion\" WHERE estado_habitacion = 'Limpieza';")
                    hab_limpieza = cur.fetchone()[0]

                    cur.execute("SELECT COUNT(*) FROM public.\"Habitacion\" WHERE estado_habitacion = 'Mantenimiento';")
                    hab_mantenimiento = cur.fetchone()[0]

                    cur.execute("SELECT COUNT(*) FROM public.\"Reserva\" WHERE fecha_hora_ingreso::date = CURRENT_DATE;")
                    llegadas_hoy = cur.fetchone()[0]

                    cur.execute("SELECT COUNT(*) FROM public.\"Reserva\" WHERE fecha_hora_salida::date = CURRENT_DATE;")
                    salidas_hoy = cur.fetchone()[0]

                    tasa_ocupacion = round((hab_ocupadas / total_habitaciones * 100), 1) if total_habitaciones > 0 else 0

                conn.close()
                self._send_json({
                    "success": True,
                    "data": {
                        "total_huespedes": total_huespedes,
                        "total_reservas": total_reservas,
                        "total_habitaciones": total_habitaciones,
                        "hab_disponibles": hab_disponibles,
                        "hab_reservadas": hab_reservadas,
                        "hab_ocupadas": hab_ocupadas,
                        "hab_limpieza": hab_limpieza,
                        "hab_mantenimiento": hab_mantenimiento,
                        "tasa_ocupacion": tasa_ocupacion,
                        "llegadas_hoy": llegadas_hoy,
                        "salidas_hoy": salidas_hoy
                    }
                })
            except Exception as e:
                self._send_error(e, 500)
            return

        # 3. API: Catálogos del Sistema
        if path == "/api/catalogos":
            try:
                conn = get_connection()
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute('SELECT "cod_tipoDoc", descripcion FROM public.tipo_doc_identidad ORDER BY "cod_tipoDoc";')
                    tipos_doc = cur.fetchall()

                    cur.execute('SELECT "cod_tipoHabitacion", descripcion, precio_habitacion FROM public.tipo_habitacion ORDER BY "cod_tipoHabitacion";')
                    tipos_hab = cur.fetchall()

                    cur.execute('SELECT "cod_medioReserva", descripcion FROM public.medio_reserva ORDER BY "cod_medioReserva";')
                    medios_reserva = cur.fetchall()

                    cur.execute('SELECT "cod_metodoPago", descripcion FROM public.metodo_pago ORDER BY "cod_metodoPago";')
                    metodos_pago = cur.fetchall()

                    cur.execute('SELECT cod_recepcionista, nombres, apellidos, rol FROM public."Recepcionista" WHERE estado = \'Activo\' ORDER BY cod_recepcionista;')
                    recepcionistas = cur.fetchall()

                conn.close()
                self._send_json({
                    "success": True,
                    "data": {
                        "tipos_documento": tipos_doc,
                        "tipos_habitacion": tipos_hab,
                        "medios_reserva": medios_reserva,
                        "metodos_pago": metodos_pago,
                        "recepcionistas": recepcionistas
                    }
                })
            except Exception as e:
                self._send_error(e, 500)
            return

        # 4. API: Directorio de Huéspedes
        if path == "/api/huespedes":
            try:
                conn = get_connection()
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("""
                        SELECT 
                            h.doc_identidad,
                            h."cod_tipoDoc",
                            td.descripcion AS tipo_doc_desc,
                            h.nombres,
                            h.apellidos,
                            h.correo,
                            STRING_AGG(DISTINCT t.num_telefono, ', ') AS telefonos,
                            COUNT(r.cod_reserva) AS total_reservas
                        FROM public."Huesped" h
                        LEFT JOIN public.tipo_doc_identidad td ON h."cod_tipoDoc" = td."cod_tipoDoc"
                        LEFT JOIN public."Telefono" t ON h.doc_identidad = t.doc_identidad
                        LEFT JOIN public."Reserva" r ON h.doc_identidad = r.doc_identidad
                        GROUP BY h.doc_identidad, h."cod_tipoDoc", td.descripcion, h.nombres, h.apellidos, h.correo
                        ORDER BY h.apellidos ASC, h.nombres ASC;
                    """)
                    huespedes = cur.fetchall()
                conn.close()
                self._send_json({"success": True, "data": huespedes})
            except Exception as e:
                self._send_error(e, 500)
            return

        # 5. API: Gestión de Reservas
        if path == "/api/reservas":
            try:
                conn = get_connection()
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("""
                        SELECT 
                            r.cod_reserva,
                            r.fecha_reserva,
                            r.hora_reserva,
                            r.fecha_hora_ingreso,
                            r.fecha_hora_salida,
                            r.solicita_desayuno,
                            r.observaciones,
                            r.doc_identidad,
                            h.nombres || ' ' || h.apellidos AS huesped_nombre,
                            h.correo AS huesped_correo,
                            STRING_AGG(DISTINCT t.num_telefono, ', ') AS huesped_telefono,
                            r."cod_medioReserva",
                            m.descripcion AS medio_reserva_desc,
                            r.cod_recepcionista,
                            e.nombres || ' ' || e.apellidos AS recepcionista_nombre,
                            hab.num_habitacion,
                            th.descripcion AS tipo_habitacion,
                            th.precio_habitacion,
                            hab.estado_habitacion
                        FROM public."Reserva" r
                        INNER JOIN public."Huesped" h ON r.doc_identidad = h.doc_identidad
                        LEFT JOIN public."Telefono" t ON h.doc_identidad = t.doc_identidad
                        INNER JOIN public.medio_reserva m ON r."cod_medioReserva" = m."cod_medioReserva"
                        INNER JOIN public."Recepcionista" e ON r.cod_recepcionista = e.cod_recepcionista
                        LEFT JOIN public."Habitacion" hab ON r.cod_reserva = hab.cod_reserva
                        LEFT JOIN public.tipo_habitacion th ON hab."cod_tipoHabitacion" = th."cod_tipoHabitacion"
                        GROUP BY 
                            r.cod_reserva, r.fecha_reserva, r.hora_reserva, r.fecha_hora_ingreso, 
                            r.fecha_hora_salida, r.solicita_desayuno, r.observaciones, r.doc_identidad, 
                            h.nombres, h.apellidos, h.correo, r."cod_medioReserva", m.descripcion, 
                            r.cod_recepcionista, e.nombres, e.apellidos, hab.num_habitacion, 
                            th.descripcion, th.precio_habitacion, hab.estado_habitacion
                        ORDER BY r.fecha_hora_ingreso DESC;
                    """)
                    reservas = cur.fetchall()
                conn.close()
                self._send_json({"success": True, "data": reservas})
            except Exception as e:
                self._send_error(e, 500)
            return

        # 6. API: Rack de Habitaciones
        if path == "/api/habitaciones":
            try:
                conn = get_connection()
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("""
                        SELECT 
                            hab.num_habitacion,
                            hab."cod_tipoHabitacion",
                            th.descripcion AS tipo_habitacion,
                            th.precio_habitacion,
                            hab.estado_habitacion,
                            hab.cod_reserva,
                            h.nombres || ' ' || h.apellidos AS huesped_asignado,
                            r.fecha_hora_ingreso,
                            r.fecha_hora_salida
                        FROM public."Habitacion" hab
                        INNER JOIN public.tipo_habitacion th ON hab."cod_tipoHabitacion" = th."cod_tipoHabitacion"
                        LEFT JOIN public."Reserva" r ON hab.cod_reserva = r.cod_reserva
                        LEFT JOIN public."Huesped" h ON r.doc_identidad = h.doc_identidad
                        ORDER BY hab.num_habitacion ASC;
                    """)
                    habitaciones = cur.fetchall()
                conn.close()
                self._send_json({"success": True, "data": habitaciones})
            except Exception as e:
                self._send_error(e, 500)
            return

        if path == "/api/habitaciones/disponibles":
            try:
                conn = get_connection()
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("""
                        SELECT 
                            hab.num_habitacion,
                            hab."cod_tipoHabitacion",
                            th.descripcion AS tipo_habitacion,
                            th.precio_habitacion,
                            hab.estado_habitacion
                        FROM public."Habitacion" hab
                        INNER JOIN public.tipo_habitacion th ON hab."cod_tipoHabitacion" = th."cod_tipoHabitacion"
                        WHERE hab.estado_habitacion = 'Disponible'
                        ORDER BY th.precio_habitacion ASC, hab.num_habitacion ASC;
                    """)
                    disponibles = cur.fetchall()
                conn.close()
                self._send_json({"success": True, "data": disponibles})
            except Exception as e:
                self._send_error(e, 500)
            return

        # 7. API: Gestión de Empleados (Solo Administrador)
        if path == "/api/empleados":
            try:
                conn = get_connection()
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("""
                        SELECT 
                            cod_recepcionista, 
                            nombres, 
                            apellidos, 
                            dni, 
                            usuario, 
                            rol, 
                            estado,
                            (SELECT COUNT(*) FROM public."Reserva" r WHERE r.cod_recepcionista = e.cod_recepcionista) AS total_reservas
                        FROM public."Recepcionista" e
                        ORDER BY cod_recepcionista ASC;
                    """)
                    empleados = cur.fetchall()
                conn.close()
                self._send_json({"success": True, "data": empleados})
            except Exception as e:
                self._send_error(e, 500)
            return

        # 8. API: Centro de Reportes (10 Reportes Oficiales SQL)
        if path.startswith("/api/reportes/"):
            report_id = path.replace("/api/reportes/", "").strip()
            self._handle_report(report_id)
            return

        # 9. API: Auditoría de Operaciones
        if path == "/api/auditoria":
            try:
                conn = get_connection()
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id_auditoria, tabla_afectada, operacion, registro_id, detalle, fecha_hora, usuario_db
                        FROM public.auditoria_operaciones
                        ORDER BY id_auditoria DESC
                        LIMIT 50;
                    """)
                    logs = cur.fetchall()
                conn.close()
                self._send_json({"success": True, "data": logs})
            except Exception as e:
                self._send_error(e, 500)
            return

        # 10. Servidor de Archivos Estáticos
        if path == "/" or path == "":
            path = "/index.html"

        file_path = os.path.normpath(os.path.join(FRONTEND_DIR, path.lstrip("/")))
        if not file_path.startswith(FRONTEND_DIR) or not os.path.exists(file_path):
            self.send_error(404, "Archivo no encontrado")
            return

        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = "application/octet-stream"

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self._set_headers(200, content_type)
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error al leer archivo: {e}")

    def _handle_report(self, report_id):
        """Ejecuta los 10 reportes oficiales de la base de datos con sus respectivos JOINs"""
        report_queries = {
            "1": {
                "titulo": "Reporte 01: Reservas Registradas en el Sistema",
                "descripcion": "Listado completo de reservas detallando huésped, recepcionista a cargo y medio de reserva.",
                "sql": """
                    SELECT
                        r.cod_reserva,
                        r.fecha_reserva,
                        h.nombres || ' ' || h.apellidos AS huesped,
                        e.nombres || ' ' || e.apellidos AS recepcionista,
                        m.descripcion AS medio_reserva
                    FROM public."Reserva" r
                    INNER JOIN public."Huesped" h ON r.doc_identidad = h.doc_identidad
                    INNER JOIN public."Recepcionista" e ON r.cod_recepcionista = e.cod_recepcionista
                    INNER JOIN public.medio_reserva m ON r."cod_medioReserva" = m."cod_medioReserva"
                    ORDER BY r.fecha_reserva DESC;
                """
            },
            "2": {
                "titulo": "Reporte 02: Habitaciones Disponibles para Venta",
                "descripcion": "Habitaciones en estado Disponible con su categoría y tarifa vigente, ordenadas por precio.",
                "sql": """
                    SELECT
                        hab.num_habitacion,
                        th.descripcion AS tipo_habitacion,
                        th.precio_habitacion
                    FROM public."Habitacion" hab
                    INNER JOIN public.tipo_habitacion th ON hab."cod_tipoHabitacion" = th."cod_tipoHabitacion"
                    WHERE hab.estado_habitacion = 'Disponible'
                    ORDER BY th.precio_habitacion ASC;
                """
            },
            "3": {
                "titulo": "Reporte 03: Huéspedes con Servicio de Desayuno",
                "descripcion": "Programación de desayunos para huéspedes con servicio contratado y fechas de estadía.",
                "sql": """
                    SELECT
                        h.doc_identidad,
                        h.nombres,
                        h.apellidos,
                        r.cod_reserva,
                        r.fecha_reserva,
                        r.fecha_hora_salida
                    FROM public."Reserva" r
                    INNER JOIN public."Huesped" h ON r.doc_identidad = h.doc_identidad
                    WHERE r.solicita_desayuno = TRUE
                    ORDER BY r.fecha_hora_salida;
                """
            },
            "4": {
                "titulo": "Reporte 04: Habitaciones sin Reserva Asociada",
                "descripcion": "Inventario de habitaciones que actualmente no cuentan con una reserva vinculada.",
                "sql": """
                    SELECT
                        hab.num_habitacion,
                        th.descripcion AS tipo_habitacion,
                        hab.estado_habitacion
                    FROM public."Habitacion" hab
                    INNER JOIN public.tipo_habitacion th ON hab."cod_tipoHabitacion" = th."cod_tipoHabitacion"
                    LEFT JOIN public."Reserva" r ON hab.cod_reserva = r.cod_reserva
                    WHERE r.cod_reserva IS NULL
                    ORDER BY hab.num_habitacion;
                """
            },
            "5": {
                "titulo": "Reporte 05: Rendimiento de Reservas por Recepcionista",
                "descripcion": "Total de reservas gestionadas por cada miembro del personal de recepción.",
                "sql": """
                    SELECT
                        e.cod_recepcionista,
                        e.nombres,
                        e.apellidos,
                        COUNT(r.cod_reserva) AS total_reservas
                    FROM public."Recepcionista" e
                    LEFT JOIN public."Reserva" r ON e.cod_recepcionista = r.cod_recepcionista
                    GROUP BY e.cod_recepcionista, e.nombres, e.apellidos
                    ORDER BY total_reservas DESC;
                """
            },
            "6": {
                "titulo": "Reporte 06: Ingresos y Volumen por Método de Pago",
                "descripcion": "Resumen financiero del importe total recaudado y transacciones por cada canal de cobro.",
                "sql": """
                    SELECT
                        mp.descripcion AS metodo_pago,
                        COUNT(p.cod_pago) AS cantidad_pagos,
                        SUM(p.monto_pago) AS total_recaudado
                    FROM public."Pago" p
                    INNER JOIN public.metodo_pago mp ON p."cod_metodoPago" = mp."cod_metodoPago"
                    GROUP BY mp."cod_metodoPago", mp.descripcion
                    ORDER BY total_recaudado DESC;
                """
            },
            "7": {
                "titulo": "Reporte 07: Total Pagado y Cobros por Reserva",
                "descripcion": "Consolidado de pagos acumulados y saldo por cada reserva, incluyendo reservas sin pagos.",
                "sql": """
                    SELECT
                        r.cod_reserva,
                        h.nombres || ' ' || h.apellidos AS huesped,
                        COUNT(p.cod_pago) AS cantidad_pagos,
                        COALESCE(SUM(p.monto_pago), 0) AS total_pagado
                    FROM public."Reserva" r
                    INNER JOIN public."Huesped" h ON r.doc_identidad = h.doc_identidad
                    LEFT JOIN public."Pago" p ON r.cod_reserva = p.cod_reserva
                    GROUP BY r.cod_reserva, h.doc_identidad, h.nombres, h.apellidos
                    ORDER BY total_pagado DESC;
                """
            },
            "8": {
                "titulo": "Reporte 08: Reservas Ingresadas en Octubre 2026",
                "descripcion": "Auditoría de reservas correspondientes a la temporada de octubre 2026 con recepcionista y canal.",
                "sql": """
                    SELECT
                        r.cod_reserva,
                        r.fecha_reserva,
                        h.nombres || ' ' || h.apellidos AS huesped,
                        m.descripcion AS canal_reserva,
                        e.nombres || ' ' || e.apellidos AS recepcionista
                    FROM public."Reserva" r
                    INNER JOIN public."Huesped" h ON r.doc_identidad = h.doc_identidad
                    INNER JOIN public.medio_reserva m ON r."cod_medioReserva" = m."cod_medioReserva"
                    INNER JOIN public."Recepcionista" e ON r.cod_recepcionista = e.cod_recepcionista
                    WHERE r.fecha_reserva >= DATE '2026-10-01' AND r.fecha_reserva < DATE '2026-11-01'
                    ORDER BY r.fecha_reserva;
                """
            },
            "9": {
                "titulo": "Reporte 09: Pagos Superiores al Promedio General",
                "descripcion": "Transacciones de alto valor que superan la media de recaudación de la empresa.",
                "sql": """
                    SELECT
                        p.cod_pago,
                        p.cod_reserva,
                        p.monto_pago,
                        mp.descripcion AS metodo_pago
                    FROM public."Pago" p
                    INNER JOIN public.metodo_pago mp ON p."cod_metodoPago" = mp."cod_metodoPago"
                    WHERE p.monto_pago > (
                        SELECT AVG(monto_pago) FROM public."Pago"
                    )
                    ORDER BY p.monto_pago DESC;
                """
            },
            "10": {
                "titulo": "Reporte 10: Reservas Pendientes de Asignación de Habitación",
                "descripcion": "Reservas confirmadas que aún no tienen una habitación física asociada en el sistema.",
                "sql": """
                    SELECT
                        r.cod_reserva,
                        r.fecha_reserva,
                        h.nombres || ' ' || h.apellidos AS huesped,
                        m.descripcion AS medio_reserva
                    FROM public."Reserva" r
                    INNER JOIN public."Huesped" h ON r.doc_identidad = h.doc_identidad
                    INNER JOIN public.medio_reserva m ON r."cod_medioReserva" = m."cod_medioReserva"
                    WHERE NOT EXISTS (
                        SELECT 1 FROM public."Habitacion" hab WHERE hab.cod_reserva = r.cod_reserva
                    )
                    ORDER BY r.fecha_reserva ASC;
                """
            }
        }

        if report_id not in report_queries:
            self._send_error(f"El reporte #{report_id} no existe.", 404)
            return

        rep = report_queries[report_id]
        try:
            conn = get_connection()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(rep["sql"])
                rows = cur.fetchall()
            conn.close()

            self._send_json({
                "success": True,
                "data": {
                    "report_id": report_id,
                    "titulo": rep["titulo"],
                    "descripcion": rep["descripcion"],
                    "total_registros": len(rows),
                    "filas": rows
                }
            })
        except Exception as e:
            self._send_error(e, 500)

    def do_POST(self):
        """Manejo de inserciones y transacciones de negocio vía Stored Procedures"""
        parsed = urlparse(self.path)
        path = parsed.path

        # 0. API: Autenticación / Login
        if path == "/api/auth/login":
            try:
                data = self._read_json_body()
                user_input = data.get("usuario", "").strip()
                password_input = data.get("password", "").strip()

                if not user_input or not password_input:
                    self._send_error("Debe ingresar usuario y contraseña.", 400)
                    return

                conn = get_connection()
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("""
                        SELECT cod_recepcionista, nombres, apellidos, dni, usuario, rol, estado
                        FROM public."Recepcionista"
                        WHERE (
                            LOWER(usuario) = LOWER(%s) 
                            OR LOWER(cod_recepcionista) = LOWER(%s)
                            OR LOWER(dni) = LOWER(%s)
                        )
                        AND (password = %s OR dni = %s)
                        AND estado = 'Activo';
                    """, (user_input, user_input, user_input, password_input, password_input))
                    user = cur.fetchone()

                conn.close()

                if user:
                    self._send_json({
                        "success": True,
                        "message": f"Bienvenido, {user['nombres']}.",
                        "data": user,
                        "user": user
                    })
                else:
                    self._send_error("Credenciales incorrectas o usuario inactivo.", 401)
            except Exception as e:
                self._send_error(e, 500)
            return

        # 1. Registrar Empleado (sp_insertar_recepcionista) - Solo Admin
        if path == "/api/empleados":
            try:
                data = self._read_json_body()
                nombres = data.get("nombres", "").strip()
                apellidos = data.get("apellidos", "").strip()
                dni = data.get("dni", "").strip()
                usuario = data.get("usuario", "").strip()
                password = data.get("password", "").strip()
                rol = data.get("rol", "Recepcionista").strip()

                if not nombres or not apellidos or not dni:
                    self._send_error("Nombres, apellidos y DNI son obligatorios.", 400)
                    return

                conn = get_connection()
                with conn.cursor() as cur:
                    cur.execute("""
                        CALL public.sp_insertar_recepcionista(%s, %s, %s, %s, %s, %s, NULL);
                    """, (nombres, apellidos, dni, usuario, password or dni, rol))
                conn.commit()
                conn.close()
                self._send_json({"success": True, "message": "Empleado registrado exitosamente en el sistema."})
            except Exception as e:
                self._send_error(e, 400)
            return

        # 2. Registrar Huésped (sp_insertar_huesped)
        if path == "/api/huespedes":
            try:
                data = self._read_json_body()
                doc = data.get("doc_identidad", "").strip()
                tipo_doc = data.get("cod_tipoDoc", "D01")
                nombres = data.get("nombres", "").strip()
                apellidos = data.get("apellidos", "").strip()
                correo = data.get("correo", "").strip()
                telefono = data.get("telefono", "").strip()

                if not doc or not nombres or not apellidos:
                    self._send_error("El documento, los nombres y los apellidos son obligatorios.", 400)
                    return

                conn = get_connection()
                with conn.cursor() as cur:
                    cur.execute(
                        "CALL public.sp_insertar_huesped(%s, %s, %s, %s, %s, %s);",
                        (doc, tipo_doc, nombres, apellidos, correo, telefono)
                    )
                conn.commit()
                conn.close()
                self._send_json({"success": True, "message": "Huésped registrado exitosamente en AlojaGest."})
            except Exception as e:
                self._send_error(e, 400)
            return

        # 3. Registrar Nueva Reserva (sp_insertar_reserva)
        if path == "/api/reservas":
            try:
                data = self._read_json_body()
                doc = data.get("doc_identidad", "").strip()
                num_hab = data.get("num_habitacion", "").strip()
                fecha_ingreso = data.get("fecha_hora_ingreso", "").strip()
                fecha_salida = data.get("fecha_hora_salida", "").strip()
                cod_medio = data.get("cod_medioReserva", "M01").strip()
                cod_recepcionista = data.get("cod_recepcionista", "E001").strip()
                solicita_desayuno = bool(data.get("solicita_desayuno", False))
                observaciones = data.get("observaciones", "Sin observaciones").strip()

                if not doc or not num_hab or not fecha_ingreso or not fecha_salida:
                    self._send_error("Huésped, habitación asignada y fechas son campos obligatorios.", 400)
                    return

                conn = get_connection()
                with conn.cursor() as cur:
                    cur.execute("""
                        CALL public.sp_insertar_reserva(
                            %s, %s, %s::timestamp, %s::timestamp, %s, %s, %s, %s, NULL
                        );
                    """, (doc, num_hab, fecha_ingreso, fecha_salida, cod_medio, cod_recepcionista, solicita_desayuno, observaciones))
                conn.commit()
                conn.close()
                self._send_json({
                    "success": True, 
                    "message": f"Reserva generada con éxito y Habitación {num_hab} reservada."
                })
            except Exception as e:
                self._send_error(e, 400)
            return

        # 4. Check-in de Huésped (sp_checkin_reserva)
        if path == "/api/reservas/checkin":
            try:
                data = self._read_json_body()
                cod_reserva = data.get("cod_reserva", "").strip()
                if not cod_reserva:
                    self._send_error("Código de reserva no especificado.", 400)
                    return

                conn = get_connection()
                with conn.cursor() as cur:
                    cur.execute("CALL public.sp_checkin_reserva(%s);", (cod_reserva,))
                conn.commit()
                conn.close()
                self._send_json({"success": True, "message": f"Check-in confirmado para reserva {cod_reserva}. Habitación ahora Ocupada."})
            except Exception as e:
                self._send_error(e, 400)
            return

        # 5. Check-out de Huésped (sp_checkout_reserva)
        if path == "/api/reservas/checkout":
            try:
                data = self._read_json_body()
                cod_reserva = data.get("cod_reserva", "").strip()
                if not cod_reserva:
                    self._send_error("Código de reserva no especificado.", 400)
                    return

                conn = get_connection()
                with conn.cursor() as cur:
                    cur.execute("CALL public.sp_checkout_reserva(%s);", (cod_reserva,))
                conn.commit()
                conn.close()
                self._send_json({"success": True, "message": f"Check-out completado para reserva {cod_reserva}. Habitación transferida a Limpieza."})
            except Exception as e:
                self._send_error(e, 400)
            return

        # 6. Cambio manual de estado de Habitación (sp_cambiar_estado_habitacion)
        if path == "/api/habitaciones/estado":
            try:
                data = self._read_json_body()
                num_hab = data.get("num_habitacion", "").strip()
                nuevo_estado = data.get("nuevo_estado", "").strip()
                if not num_hab or not nuevo_estado:
                    self._send_error("Número de habitación y nuevo estado son obligatorios.", 400)
                    return

                conn = get_connection()
                with conn.cursor() as cur:
                    cur.execute("CALL public.sp_cambiar_estado_habitacion(%s, %s, NULL);", (num_hab, nuevo_estado))
                conn.commit()
                conn.close()
                self._send_json({"success": True, "message": f"Habitación {num_hab} actualizada a '{nuevo_estado}'."})
            except Exception as e:
                self._send_error(e, 400)
            return

        self.send_error(404, "Ruta no encontrada")

    def do_PUT(self):
        """Manejo de actualizaciones de registros vía Stored Procedures"""
        parsed = urlparse(self.path)
        path = parsed.path

        # 1. Modificar Empleado (sp_modificar_recepcionista)
        if path == "/api/empleados":
            try:
                data = self._read_json_body()
                cod = data.get("cod_recepcionista", "").strip()
                nombres = data.get("nombres", "").strip()
                apellidos = data.get("apellidos", "").strip()
                dni = data.get("dni", "").strip()
                usuario = data.get("usuario", "").strip()
                password = data.get("password", "").strip()
                rol = data.get("rol", "Recepcionista").strip()
                estado = data.get("estado", "Activo").strip()

                if not cod:
                    self._send_error("Código de empleado es requerido.", 400)
                    return

                conn = get_connection()
                with conn.cursor() as cur:
                    cur.execute("""
                        CALL public.sp_modificar_recepcionista(%s, %s, %s, %s, %s, %s, %s, %s);
                    """, (cod, nombres, apellidos, dni, usuario, password, rol, estado))
                conn.commit()
                conn.close()
                self._send_json({"success": True, "message": "Datos de empleado actualizados con éxito."})
            except Exception as e:
                self._send_error(e, 400)
            return

        # 2. Modificar Huésped
        if path == "/api/huespedes":
            try:
                data = self._read_json_body()
                doc = data.get("doc_identidad", "").strip()
                tipo_doc = data.get("cod_tipoDoc", "D01")
                nombres = data.get("nombres", "").strip()
                apellidos = data.get("apellidos", "").strip()
                correo = data.get("correo", "").strip()
                telefono = data.get("telefono", "").strip()

                if not doc:
                    self._send_error("El documento de identidad es requerido.", 400)
                    return

                conn = get_connection()
                with conn.cursor() as cur:
                    cur.execute(
                        "CALL public.sp_modificar_huesped(%s, %s, %s, %s, %s, %s);",
                        (doc, tipo_doc, nombres, apellidos, correo, telefono)
                    )
                conn.commit()
                conn.close()
                self._send_json({"success": True, "message": "Datos de huésped actualizados con éxito."})
            except Exception as e:
                self._send_error(e, 400)
            return

        # 3. Modificar Reserva
        if path == "/api/reservas":
            try:
                data = self._read_json_body()
                cod_reserva = data.get("cod_reserva", "").strip()
                num_hab = data.get("num_habitacion", "").strip()
                fecha_ingreso = data.get("fecha_hora_ingreso", "").strip()
                fecha_salida = data.get("fecha_hora_salida", "").strip()
                cod_medio = data.get("cod_medioReserva", "").strip()
                solicita_desayuno = bool(data.get("solicita_desayuno", False))
                observaciones = data.get("observaciones", "").strip()

                if not cod_reserva or not fecha_ingreso or not fecha_salida:
                    self._send_error("Código de reserva y fechas son obligatorios.", 400)
                    return

                conn = get_connection()
                with conn.cursor() as cur:
                    cur.execute("""
                        CALL public.sp_modificar_reserva(
                            %s, %s, %s::timestamp, %s::timestamp, %s, %s, %s
                        );
                    """, (cod_reserva, num_hab, fecha_ingreso, fecha_salida, cod_medio, solicita_desayuno, observaciones))
                conn.commit()
                conn.close()
                self._send_json({"success": True, "message": f"Reserva {cod_reserva} actualizada exitosamente."})
            except Exception as e:
                self._send_error(e, 400)
            return

        self.send_error(404, "Ruta no encontrada")

    def do_DELETE(self):
        """Manejo de bajas y cancelaciones vía Stored Procedures"""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # 1. Dar de baja / Eliminar Empleado (sp_eliminar_recepcionista)
        if path == "/api/empleados":
            try:
                cod = query.get("cod_recepcionista", [""])[0].strip()
                if not cod:
                    data = self._read_json_body()
                    cod = data.get("cod_recepcionista", "").strip()

                if not cod:
                    self._send_error("Código de empleado no especificado.", 400)
                    return

                conn = get_connection()
                with conn.cursor() as cur:
                    cur.execute("CALL public.sp_eliminar_recepcionista(%s);", (cod,))
                conn.commit()
                conn.close()
                self._send_json({"success": True, "message": "Empleado desactivado del sistema."})
            except Exception as e:
                self._send_error(e, 400)
            return

        # 2. Eliminar Huésped
        if path == "/api/huespedes":
            try:
                doc = query.get("doc_identidad", [""])[0].strip()
                if not doc:
                    data = self._read_json_body()
                    doc = data.get("doc_identidad", "").strip()

                if not doc:
                    self._send_error("Documento de identidad no especificado.", 400)
                    return

                conn = get_connection()
                with conn.cursor() as cur:
                    cur.execute("CALL public.sp_eliminar_huesped(%s);", (doc,))
                conn.commit()
                conn.close()
                self._send_json({"success": True, "message": "Huésped eliminado del sistema."})
            except Exception as e:
                self._send_error(e, 400)
            return

        # 3. Cancelar Reserva
        if path == "/api/reservas":
            try:
                cod_reserva = query.get("cod_reserva", [""])[0].strip()
                if not cod_reserva:
                    data = self._read_json_body()
                    cod_reserva = data.get("cod_reserva", "").strip()

                if not cod_reserva:
                    self._send_error("Código de reserva no especificado.", 400)
                    return

                conn = get_connection()
                with conn.cursor() as cur:
                    cur.execute("CALL public.sp_cancelar_reserva(%s);", (cod_reserva,))
                conn.commit()
                conn.close()
                self._send_json({"success": True, "message": f"Reserva {cod_reserva} cancelada y habitación liberada."})
            except Exception as e:
                self._send_error(e, 400)
            return

        self.send_error(404, "Ruta no encontrada")

def start_server():
    server_address = (SERVER_CONFIG["host"], SERVER_CONFIG["port"])
    httpd = ThreadedHTTPServer(server_address, AlojaGestHandler)
    print("=" * 70)
    print("   ALOJAGEST - SISTEMA INTEGRAL DE GESTIÓN HOTELERA")
    print(f"   URL del Sistema: http://{SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}")
    print(f"   Base de Datos: PostgreSQL ({SERVER_CONFIG['host']}:{SERVER_CONFIG['port']})")
    print("   Servidor: Multihilo Nativo Activo (Sin Frameworks)")
    print("=" * 70)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor AlojaGest detenido de forma segura.")
        httpd.server_close()

if __name__ == "__main__":
    start_server()
