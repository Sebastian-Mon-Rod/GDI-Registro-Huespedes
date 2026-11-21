-- ========================================================
-- HOTEL CUMBRE REAL AIRPORT - ESQUEMA DE BASE DE DATOS
-- Modelo Relacional Normalizado en 3FN
-- Compatible con PostgreSQL 14+ / 18+
-- ========================================================

-- 1. SECUENCIAS
CREATE SEQUENCE IF NOT EXISTS public.recepcionista_codigo_seq
    START WITH 1 MINVALUE 1 MAXVALUE 999 NO CYCLE;

CREATE SEQUENCE IF NOT EXISTS public.reserva_codigo_seq
    START WITH 1 MINVALUE 1 MAXVALUE 99999 NO CYCLE;

CREATE SEQUENCE IF NOT EXISTS public.pago_codigo_seq
    START WITH 1 MINVALUE 1 MAXVALUE 99999 NO CYCLE;

-- 2. TABLAS DE CATÁLOGO
CREATE TABLE IF NOT EXISTS public.tipo_doc_identidad (
    "cod_tipoDoc" VARCHAR(3) PRIMARY KEY,
    descripcion VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.tipo_habitacion (
    "cod_tipoHabitacion" VARCHAR(3) PRIMARY KEY,
    descripcion VARCHAR(15) NOT NULL,
    precio_habitacion NUMERIC(5,2) NOT NULL CHECK (precio_habitacion >= 0)
);

CREATE TABLE IF NOT EXISTS public.metodo_pago (
    "cod_metodoPago" VARCHAR(4) PRIMARY KEY,
    descripcion VARCHAR(25) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.medio_reserva (
    "cod_medioReserva" VARCHAR(3) PRIMARY KEY,
    descripcion VARCHAR(10) NOT NULL
);

-- 3. TABLA: Recepcionista
CREATE TABLE IF NOT EXISTS public."Recepcionista" (
    cod_recepcionista VARCHAR(4) PRIMARY KEY 
        DEFAULT ('E' || LPAD(NEXTVAL('public.recepcionista_codigo_seq')::TEXT, 3, '0')),
    nombres VARCHAR(255) NOT NULL,
    apellidos VARCHAR(255) NOT NULL
);

-- 4. TABLA: Huésped
CREATE TABLE IF NOT EXISTS public."Huesped" (
    doc_identidad VARCHAR(20) PRIMARY KEY,
    "cod_tipoDoc" VARCHAR(3) NOT NULL,
    nombres VARCHAR(255) NOT NULL,
    apellidos VARCHAR(255) NOT NULL,
    correo VARCHAR(100),
    CONSTRAINT fk_huesped_tipo_doc 
        FOREIGN KEY ("cod_tipoDoc") REFERENCES public.tipo_doc_identidad ("cod_tipoDoc")
);

-- 5. TABLA: Reserva
CREATE TABLE IF NOT EXISTS public."Reserva" (
    cod_reserva VARCHAR(6) PRIMARY KEY 
        DEFAULT ('R' || LPAD(NEXTVAL('public.reserva_codigo_seq')::TEXT, 5, '0')),
    fecha_reserva DATE NOT NULL,
    hora_reserva TIME NOT NULL,
    fecha_hora_ingreso TIMESTAMP NOT NULL,
    fecha_hora_salida TIMESTAMP NOT NULL,
    "cod_medioReserva" VARCHAR(3) NOT NULL,
    observaciones VARCHAR(128),
    solicita_desayuno BOOLEAN NOT NULL,
    doc_identidad VARCHAR(20) NOT NULL,
    cod_recepcionista VARCHAR(4) NOT NULL,
    CONSTRAINT fk_reserva_medio 
        FOREIGN KEY ("cod_medioReserva") REFERENCES public.medio_reserva ("cod_medioReserva"),
    CONSTRAINT fk_reserva_huesped 
        FOREIGN KEY (doc_identidad) REFERENCES public."Huesped" (doc_identidad) ON DELETE CASCADE,
    CONSTRAINT fk_reserva_recepcionista 
        FOREIGN KEY (cod_recepcionista) REFERENCES public."Recepcionista" (cod_recepcionista)
);

-- 6. TABLA: Habitación
CREATE TABLE IF NOT EXISTS public."Habitacion" (
    num_habitacion VARCHAR(4) PRIMARY KEY,
    "cod_tipoHabitacion" VARCHAR(3) NOT NULL,
    estado_habitacion VARCHAR(15) NOT NULL,
    cod_reserva VARCHAR(6),
    CONSTRAINT fk_habitacion_tipo 
        FOREIGN KEY ("cod_tipoHabitacion") REFERENCES public.tipo_habitacion ("cod_tipoHabitacion"),
    CONSTRAINT fk_habitacion_reserva 
        FOREIGN KEY (cod_reserva) REFERENCES public."Reserva" (cod_reserva) ON DELETE SET NULL
);

-- 7. TABLA: Pago
CREATE TABLE IF NOT EXISTS public."Pago" (
    cod_pago VARCHAR(6) PRIMARY KEY 
        DEFAULT ('P' || LPAD(NEXTVAL('public.pago_codigo_seq')::TEXT, 5, '0')),
    monto_pago NUMERIC(7,2) NOT NULL CHECK (monto_pago >= 0),
    "cod_metodoPago" VARCHAR(4) NOT NULL,
    cod_reserva VARCHAR(6) NOT NULL,
    cod_recepcionista VARCHAR(4) NOT NULL,
    CONSTRAINT fk_pago_metodo 
        FOREIGN KEY ("cod_metodoPago") REFERENCES public.metodo_pago ("cod_metodoPago"),
    CONSTRAINT fk_pago_reserva 
        FOREIGN KEY (cod_reserva) REFERENCES public."Reserva" (cod_reserva) ON DELETE CASCADE,
    CONSTRAINT fk_pago_recepcionista 
        FOREIGN KEY (cod_recepcionista) REFERENCES public."Recepcionista" (cod_recepcionista)
);

-- 8. TABLA: Teléfono (atributo multivaluado de Huésped)
CREATE TABLE IF NOT EXISTS public."Telefono" (
    doc_identidad VARCHAR(20) NOT NULL,
    num_telefono VARCHAR(20) NOT NULL,
    CONSTRAINT pk_telefono PRIMARY KEY (doc_identidad, num_telefono),
    CONSTRAINT fk_telefono_huesped 
        FOREIGN KEY (doc_identidad) REFERENCES public."Huesped" (doc_identidad) ON DELETE CASCADE
);

-- 9. ASIGNACIÓN DE DUEÑO DE SECUENCIAS
ALTER SEQUENCE recepcionista_codigo_seq OWNED BY public."Recepcionista".cod_recepcionista;
ALTER SEQUENCE reserva_codigo_seq OWNED BY public."Reserva".cod_reserva;
ALTER SEQUENCE pago_codigo_seq OWNED BY public."Pago".cod_pago;

-- 10. ÍNDICES SECUNDARIOS B-TREE
CREATE INDEX IF NOT EXISTS idx_habitacion_estado ON public."Habitacion" USING BTREE (estado_habitacion);
CREATE INDEX IF NOT EXISTS idx_pago_reserva ON public."Pago" USING BTREE (cod_reserva);
CREATE INDEX IF NOT EXISTS idx_reserva_fecha ON public."Reserva" USING BTREE (fecha_reserva);
