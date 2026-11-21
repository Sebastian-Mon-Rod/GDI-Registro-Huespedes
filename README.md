# AlojaGest &middot; Sistema Integral de Gestión Hotelera

**AlojaGest** es una solución de software empresarial diseñada para optimizar y centralizar la administración hotelera, el control del ciclo de vida de reservas, la gestión de huéspedes y el monitoreo en tiempo real de la disponibilidad de habitaciones.

Diseñado con un enfoque de alto rendimiento, confiabilidad y arquitectura limpia, AlojaGest opera directamente sobre **PostgreSQL**, garantizando integridad transaccional mediante **Procedimientos Almacenados** y **Triggers** en la base de datos, sin dependencias de frameworks externos pesados.

---

## 🌟 Características Principales

### 1. Panel Ejecutivo y Dashboard en Tiempo Real
* **Métricas Clave (KPIs):** Tasa de ocupación porcentual, habitaciones disponibles, reservadas, en estadía (ocupadas) y en limpieza.
* **Control de Flujo Diario:** Indicadores de Check-ins y Check-outs programados para la fecha.
* **Distribución de Capacidad:** Gráfico de ocupación en tiempo real.

### 2. Rack Interactivo de Habitaciones (Room Matrix)
* Mapa visual de ocupación con código de colores según el estándar hotelero internacional.
* Asignación inmediata de reservas con 1 solo clic sobre cualquier habitación libre.
* Rehabilitación inmediata de habitaciones tras proceso de aseo (*Limpieza* &rarr; *Disponible*).

### 3. Gestión y Ciclo de Vida de Reservas
* **Emisión Asistida de Reservas:** Asignación automática de tarifas por categoría, cálculo de noches, validación de fechas de ingreso/salida y registro de servicios complementarios (desayuno buffet, cochera, requerimientos especiales).
* **Operaciones en 1 Clic:**
  * 🛎️ **Check-in:** Registro de llegada del cliente y pase automático de la habitación a *Ocupada*.
  * 🚪 **Check-out:** Conclusión de la estadía, liberación de reserva y pase de la habitación a *Limpieza*.
  * 📄 **Emisión de Voucher:** Generación de comprobante imprimible con desglose de servicios.
  * ✏️ **Modificación y Cancelación:** Ajuste de fechas o anulación con liberación inmediata del inventario.

### 4. Directorio Corporativo de Huéspedes
* Fichero centralizado de clientes con documento de identidad (DNI, Pasaporte, Carnet de Extranjería), teléfonos de contacto, correo y récord histórico de estadías.

### 5. Centro de Reportes y Business Intelligence (BI)
Visualizador interactivo con 10 reportes corporativos basados en consultas relacionales complejas (`JOINs`, agrupaciones y subconsultas):
1. **Reporte 01:** Registro cronológico de reservas detalladas con huésped, recepcionista y canal.
2. **Reporte 02:** Inventario de habitaciones disponibles con tarifas ordenadas.
3. **Reporte 03:** Programación de huéspedes con servicio de desayuno buffet contratado.
4. **Reporte 04:** Capacidad remanente de habitaciones sin reserva asignada.
5. **Reporte 05:** Rendimiento y productividad por recepcionista en turno.
6. **Reporte 06:** Recaudación acumulada y volumen por método de cobro.
7. **Reporte 07:** Consolidado financiero de pagos asociados a cada reserva.
8. **Reporte 08:** Auditoría de reservas por período comercial.
9. **Reporte 09:** Detección de transacciones superiores al promedio general de caja.
10. **Reporte 10:** Reservas confirmadas pendientes de asignación de habitación física.

### 6. Seguridad y Auditoría Operativa
* Bitácora en caliente que registra automáticamente cada inserción, modificación, check-in, check-out y cancelación ejecutada en el motor de base de datos.

---

## 🏛️ Arquitectura Técnica

```text
┌────────────────────────────────────────────────────────┐
│             ALOJAGEST FRONTEND (Vanilla)              │
│       HTML5 Semántico &middot; CSS3 Moderno &middot; JS Puro       │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / JSON REST
┌───────────────────────────▼────────────────────────────┐
│              ALOJAGEST BACKEND ENGINE                  │
│       Python Nativo (http.server) - Cero Frameworks    │
└───────────────────────────┬────────────────────────────┘
                            │ psycopg2 (Conector Nativo)
┌───────────────────────────▼────────────────────────────┐
│             POSTGRESQL 14+ / 18+ DATABASE              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Modelo Relacional Normalizado en 3FN (10 Tablas) │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ Procedimientos Almacenados (CRUD y Lógica Op.)   │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ Triggers de Validación, Sincronización y Auditoría│ │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura del Software

```text
app/
├── backend/
│   ├── config.py              # Parámetros de conexión y servidor
│   ├── db.py                  # Módulo de base de datos y diagnóstico
│   ├── server.py              # Servidor HTTP nativo y API REST AlojaGest
│   ├── test_connection.py     # Diagnóstico de conectividad con PostgreSQL
│   └── test_crud_sp.py        # Suite de pruebas automatizadas de Procedimientos
├── database/
│   ├── schema.sql             # Definición de tablas en 3FN, secuencias e índices
│   ├── seeds.sql              # Registros semilla de prueba inicial
│   ├── procedures_triggers.sql# Lógica de Procedimientos Almacenados y Triggers
│   └── init_db.py             # Inicializador automático de la base de datos
├── frontend/
│   ├── index.html             # Terminal de usuario de AlojaGest
│   ├── styles.css             # Hoja de estilos corporativa
│   └── app.js                 # Lógica interactiva en Vanilla JavaScript
├── run.bat                    # Script ejecutable de 1 clic para Windows
└── README.md                  # Manual del sistema
```

---

## ⚡ Guía de Puesta en Marcha

### Requisitos Previos
1. **Python 3.10+** instalado.
2. **PostgreSQL 14+ / 18+** en ejecución en el puerto estándar `5432`.
3. Librería `psycopg2` instalada (`pip install psycopg2-binary`).

### Inicialización y Arranque
1. **Iniciar el Servidor AlojaGest:**
   * Haz doble clic en el archivo `run.bat` (o ejecuta `python app/backend/server.py`).
   * Este descargara todas las dependencias que se necesiten donde la parte 3/7 la cual es de la BD demora entre 7 a 8 min.
2. **Acceder a la Terminal Web:**
   * Abre tu navegador e ingresa a: **[http://localhost:8000](http://localhost:8000)**.
