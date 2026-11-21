-- ========================================================
-- HOTEL CUMBRE REAL AIRPORT - PROCEDIMIENTOS Y TRIGGERS
-- Requerimiento: CRUD completo mediante Procedures y Triggers
-- ========================================================

-- 1. TABLA DE AUDITORÍA (Respaldada por Triggers)
CREATE TABLE IF NOT EXISTS public.auditoria_operaciones (
    id_auditoria SERIAL PRIMARY KEY,
    tabla_afectada VARCHAR(50) NOT NULL,
    operacion VARCHAR(15) NOT NULL,
    registro_id VARCHAR(50) NOT NULL,
    detalle TEXT,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_db VARCHAR(50) DEFAULT CURRENT_USER
);

-- ========================================================
-- TRIGGERS DE VALIDACIÓN Y CONTROL DE NEGOCIO
-- ========================================================

-- Trigger 1: Validación de fechas y consistencia en Reservas
CREATE OR REPLACE FUNCTION public.fn_validar_reserva()
RETURNS TRIGGER AS $$
BEGIN
    -- Validar que la fecha/hora de salida sea posterior a la de ingreso
    IF NEW.fecha_hora_salida <= NEW.fecha_hora_ingreso THEN
        RAISE EXCEPTION 'La fecha y hora de salida (%) debe ser posterior a la de ingreso (%).',
            NEW.fecha_hora_salida, NEW.fecha_hora_ingreso;
    END IF;

    -- Normalizar observaciones si es nulo
    IF NEW.observaciones IS NULL THEN
        NEW.observaciones := 'Sin observaciones';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_validar_reserva ON public."Reserva";
CREATE TRIGGER trg_validar_reserva
BEFORE INSERT OR UPDATE ON public."Reserva"
FOR EACH ROW
EXECUTE FUNCTION public.fn_validar_reserva();


-- Trigger 2: Auditoría automática de cambios en Reservas
CREATE OR REPLACE FUNCTION public.fn_auditar_reserva()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO public.auditoria_operaciones(tabla_afectada, operacion, registro_id, detalle)
        VALUES ('Reserva', 'INSERT', NEW.cod_reserva, 'Nueva reserva para huésped: ' || NEW.doc_identidad);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO public.auditoria_operaciones(tabla_afectada, operacion, registro_id, detalle)
        VALUES ('Reserva', 'UPDATE', NEW.cod_reserva, 'Modificación de reserva. Fechas: ' || NEW.fecha_hora_ingreso || ' a ' || NEW.fecha_hora_salida);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO public.auditoria_operaciones(tabla_afectada, operacion, registro_id, detalle)
        VALUES ('Reserva', 'DELETE', OLD.cod_reserva, 'Cancelación/eliminación de reserva del huésped: ' || OLD.doc_identidad);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_auditar_reserva ON public."Reserva";
CREATE TRIGGER trg_auditar_reserva
AFTER INSERT OR UPDATE OR DELETE ON public."Reserva"
FOR EACH ROW
EXECUTE FUNCTION public.fn_auditar_reserva();


-- Trigger 3: Sincronización automática de estado de Habitaciones al cambiar reservas
CREATE OR REPLACE FUNCTION public.fn_sincronizar_estado_habitacion()
RETURNS TRIGGER AS $$
BEGIN
    -- Si se asigna una reserva y el estado estaba Disponible, pasa a Reservada
    IF NEW.cod_reserva IS NOT NULL AND (OLD.cod_reserva IS NULL OR OLD.cod_reserva <> NEW.cod_reserva) THEN
        IF NEW.estado_habitacion = 'Disponible' THEN
            NEW.estado_habitacion := 'Reservada';
        END IF;
    -- Si se desvincula la reserva, pasa a Limpieza para revisión
    ELSIF NEW.cod_reserva IS NULL AND OLD.cod_reserva IS NOT NULL THEN
        IF NEW.estado_habitacion IN ('Reservada', 'Ocupada') THEN
            NEW.estado_habitacion := 'Limpieza';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sincronizar_estado_habitacion ON public."Habitacion";
CREATE TRIGGER trg_sincronizar_estado_habitacion
BEFORE UPDATE ON public."Habitacion"
FOR EACH ROW
EXECUTE FUNCTION public.fn_sincronizar_estado_habitacion();


-- ========================================================
-- PROCEDIMIENTOS ALMACENADOS PARA OPERACIONES CRUD
-- ========================================================

-- PROCEDIMIENTO 1: Insertar Huésped (con teléfono)
CREATE OR REPLACE PROCEDURE public.sp_insertar_huesped(
    IN p_doc VARCHAR(20),
    IN p_tipo_doc VARCHAR(3),
    IN p_nombres VARCHAR(255),
    IN p_apellidos VARCHAR(255),
    IN p_correo VARCHAR(100),
    IN p_telefono VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Validar documento no vacío
    IF p_doc IS NULL OR TRIM(p_doc) = '' THEN
        RAISE EXCEPTION 'El documento de identidad no puede estar vacío.';
    END IF;

    -- Insertar en Huesped
    INSERT INTO public."Huesped" (doc_identidad, "cod_tipoDoc", nombres, apellidos, correo)
    VALUES (p_doc, p_tipo_doc, p_nombres, p_apellidos, p_correo);

    -- Insertar teléfono si se proporcionó
    IF p_telefono IS NOT NULL AND TRIM(p_telefono) <> '' THEN
        INSERT INTO public."Telefono" (doc_identidad, num_telefono)
        VALUES (p_doc, TRIM(p_telefono))
        ON CONFLICT DO NOTHING;
    END IF;

    -- Registrar auditoría
    INSERT INTO public.auditoria_operaciones(tabla_afectada, operacion, registro_id, detalle)
    VALUES ('Huesped', 'INSERT', p_doc, 'Registro de nuevo huésped: ' || p_nombres || ' ' || p_apellidos);
END;
$$;


-- PROCEDIMIENTO 2: Modificar Huésped (con teléfono)
CREATE OR REPLACE PROCEDURE public.sp_modificar_huesped(
    IN p_doc VARCHAR(20),
    IN p_tipo_doc VARCHAR(3),
    IN p_nombres VARCHAR(255),
    IN p_apellidos VARCHAR(255),
    IN p_correo VARCHAR(100),
    IN p_telefono VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE public."Huesped"
    SET "cod_tipoDoc" = p_tipo_doc,
        nombres = p_nombres,
        apellidos = p_apellidos,
        correo = p_correo
    WHERE doc_identidad = p_doc;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Huésped con documento % no existe.', p_doc;
    END IF;

    -- Actualizar o agregar teléfono
    IF p_telefono IS NOT NULL AND TRIM(p_telefono) <> '' THEN
        -- Si ya tiene teléfonos, actualizamos el primero, o insertamos
        IF EXISTS (SELECT 1 FROM public."Telefono" WHERE doc_identidad = p_doc) THEN
            UPDATE public."Telefono" 
            SET num_telefono = TRIM(p_telefono)
            WHERE doc_identidad = p_doc;
        ELSE
            INSERT INTO public."Telefono" (doc_identidad, num_telefono)
            VALUES (p_doc, TRIM(p_telefono));
        END IF;
    END IF;

    -- Registrar auditoría
    INSERT INTO public.auditoria_operaciones(tabla_afectada, operacion, registro_id, detalle)
    VALUES ('Huesped', 'UPDATE', p_doc, 'Actualización de datos del huésped: ' || p_nombres || ' ' || p_apellidos);
END;
$$;


-- PROCEDIMIENTO 3: Eliminar Huésped
CREATE OR REPLACE PROCEDURE public.sp_eliminar_huesped(
    IN p_doc VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Verificar si existe
    IF NOT EXISTS (SELECT 1 FROM public."Huesped" WHERE doc_identidad = p_doc) THEN
        RAISE EXCEPTION 'Huésped con documento % no existe.', p_doc;
    END IF;

    -- Desvincular habitaciones de reservas de este huésped
    UPDATE public."Habitacion"
    SET cod_reserva = NULL, estado_habitacion = 'Disponible'
    WHERE cod_reserva IN (SELECT cod_reserva FROM public."Reserva" WHERE doc_identidad = p_doc);

    -- Eliminar huésped (cascada en Telefono, Reserva y Pago por FKs)
    DELETE FROM public."Huesped" WHERE doc_identidad = p_doc;

    -- Registrar auditoría
    INSERT INTO public.auditoria_operaciones(tabla_afectada, operacion, registro_id, detalle)
    VALUES ('Huesped', 'DELETE', p_doc, 'Eliminación del huésped y dependencias');
END;
$$;


-- PROCEDIMIENTO 4: Cambiar estado de Habitación
CREATE OR REPLACE PROCEDURE public.sp_cambiar_estado_habitacion(
    IN p_num VARCHAR(4),
    IN p_nuevo_estado VARCHAR(15),
    IN p_cod_reserva VARCHAR(6) DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public."Habitacion" WHERE num_habitacion = p_num) THEN
        RAISE EXCEPTION 'Habitación % no encontrada.', p_num;
    END IF;

    UPDATE public."Habitacion"
    SET estado_habitacion = p_nuevo_estado,
        cod_reserva = p_cod_reserva
    WHERE num_habitacion = p_num;

    INSERT INTO public.auditoria_operaciones(tabla_afectada, operacion, registro_id, detalle)
    VALUES ('Habitacion', 'UPDATE', p_num, 'Cambio de estado a: ' || p_nuevo_estado || ' (Reserva: ' || COALESCE(p_cod_reserva, 'Ninguna') || ')');
END;
$$;


-- ========================================================
-- PROCEDIMIENTOS ALMACENADOS PARA RESERVAS (70% FUNCIONALIDAD)
-- ========================================================

-- PROCEDIMIENTO 5: Insertar Reserva con Asignación de Habitación
CREATE OR REPLACE PROCEDURE public.sp_insertar_reserva(
    IN p_doc VARCHAR(20),
    IN p_num_habitacion VARCHAR(4),
    IN p_fecha_ingreso TIMESTAMP,
    IN p_fecha_salida TIMESTAMP,
    IN p_cod_medio VARCHAR(3),
    IN p_cod_recepcionista VARCHAR(4),
    IN p_solicita_desayuno BOOLEAN,
    IN p_observaciones VARCHAR(128),
    INOUT p_cod_reserva VARCHAR(6) DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_nuevo_cod VARCHAR(6);
    v_estado_actual VARCHAR(15);
BEGIN
    -- 1. Validar que exista el huésped
    IF NOT EXISTS (SELECT 1 FROM public."Huesped" WHERE doc_identidad = p_doc) THEN
        RAISE EXCEPTION 'El huésped con documento % no está registrado.', p_doc;
    END IF;

    -- 2. Validar que la habitación exista y esté disponible
    SELECT estado_habitacion INTO v_estado_actual
    FROM public."Habitacion"
    WHERE num_habitacion = p_num_habitacion;

    IF v_estado_actual IS NULL THEN
        RAISE EXCEPTION 'La habitación % no existe.', p_num_habitacion;
    END IF;

    IF v_estado_actual NOT IN ('Disponible', 'Limpieza') THEN
        RAISE EXCEPTION 'La habitación % no se encuentra disponible (Estado actual: %).', p_num_habitacion, v_estado_actual;
    END IF;

    -- 3. Generar código de reserva si no viene dado
    IF p_cod_reserva IS NULL OR p_cod_reserva = '' THEN
        v_nuevo_cod := 'R' || LPAD(NEXTVAL('public.reserva_codigo_seq')::TEXT, 5, '0');
    ELSE
        v_nuevo_cod := p_cod_reserva;
    END IF;
    p_cod_reserva := v_nuevo_cod;

    -- 4. Insertar en tabla Reserva
    INSERT INTO public."Reserva" (
        cod_reserva, fecha_reserva, hora_reserva, fecha_hora_ingreso,
        fecha_hora_salida, "cod_medioReserva", observaciones,
        solicita_desayuno, doc_identidad, cod_recepcionista
    ) VALUES (
        v_nuevo_cod, CURRENT_DATE, CURRENT_TIME, p_fecha_ingreso,
        p_fecha_salida, p_cod_medio, COALESCE(p_observaciones, 'Sin observaciones'),
        p_solicita_desayuno, p_doc, p_cod_recepcionista
    );

    -- 5. Asignar habitación y actualizar estado a 'Reservada'
    UPDATE public."Habitacion"
    SET cod_reserva = v_nuevo_cod,
        estado_habitacion = 'Reservada'
    WHERE num_habitacion = p_num_habitacion;

END;
$$;


-- PROCEDIMIENTO 6: Modificar Reserva
CREATE OR REPLACE PROCEDURE public.sp_modificar_reserva(
    IN p_cod_reserva VARCHAR(6),
    IN p_num_habitacion VARCHAR(4),
    IN p_fecha_ingreso TIMESTAMP,
    IN p_fecha_salida TIMESTAMP,
    IN p_cod_medio VARCHAR(3),
    IN p_solicita_desayuno BOOLEAN,
    IN p_observaciones VARCHAR(128)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_hab_anterior VARCHAR(4);
BEGIN
    -- Validar existencia
    IF NOT EXISTS (SELECT 1 FROM public."Reserva" WHERE cod_reserva = p_cod_reserva) THEN
        RAISE EXCEPTION 'Reserva % no encontrada.', p_cod_reserva;
    END IF;

    -- Actualizar campos de la reserva
    UPDATE public."Reserva"
    SET fecha_hora_ingreso = p_fecha_ingreso,
        fecha_hora_salida = p_fecha_salida,
        "cod_medioReserva" = p_cod_medio,
        solicita_desayuno = p_solicita_desayuno,
        observaciones = p_observaciones
    WHERE cod_reserva = p_cod_reserva;

    -- Manejar cambio de habitación si aplica
    IF p_num_habitacion IS NOT NULL AND p_num_habitacion <> '' THEN
        SELECT num_habitacion INTO v_hab_anterior
        FROM public."Habitacion"
        WHERE cod_reserva = p_cod_reserva;

        IF v_hab_anterior IS DISTINCT FROM p_num_habitacion THEN
            -- Liberar la anterior
            IF v_hab_anterior IS NOT NULL THEN
                UPDATE public."Habitacion"
                SET cod_reserva = NULL, estado_habitacion = 'Disponible'
                WHERE num_habitacion = v_hab_anterior;
            END IF;

            -- Asignar la nueva
            UPDATE public."Habitacion"
            SET cod_reserva = p_cod_reserva, estado_habitacion = 'Reservada'
            WHERE num_habitacion = p_num_habitacion;
        END IF;
    END IF;
END;
$$;


-- PROCEDIMIENTO 7: Cancelar / Eliminar Reserva
CREATE OR REPLACE PROCEDURE public.sp_cancelar_reserva(
    IN p_cod_reserva VARCHAR(6)
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public."Reserva" WHERE cod_reserva = p_cod_reserva) THEN
        RAISE EXCEPTION 'Reserva % no encontrada.', p_cod_reserva;
    END IF;

    -- Liberar habitación
    UPDATE public."Habitacion"
    SET cod_reserva = NULL,
        estado_habitacion = 'Disponible'
    WHERE cod_reserva = p_cod_reserva;

    -- Eliminar la reserva (activará trigger de auditoría trg_auditar_reserva)
    DELETE FROM public."Reserva" WHERE cod_reserva = p_cod_reserva;
END;
$$;


-- PROCEDIMIENTO 8: Check-in de Huésped (Pasa habitación a Ocupada)
CREATE OR REPLACE PROCEDURE public.sp_checkin_reserva(
    IN p_cod_reserva VARCHAR(6)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_num_hab VARCHAR(4);
BEGIN
    SELECT num_habitacion INTO v_num_hab
    FROM public."Habitacion"
    WHERE cod_reserva = p_cod_reserva;

    IF v_num_hab IS NULL THEN
        RAISE EXCEPTION 'La reserva % no tiene habitación asignada para check-in.', p_cod_reserva;
    END IF;

    UPDATE public."Habitacion"
    SET estado_habitacion = 'Ocupada'
    WHERE num_habitacion = v_num_hab;

    INSERT INTO public.auditoria_operaciones(tabla_afectada, operacion, registro_id, detalle)
    VALUES ('Habitacion', 'CHECKIN', v_num_hab, 'Check-in procesado para reserva ' || p_cod_reserva || '. Habitación ahora Ocupada.');
END;
$$;


-- PROCEDIMIENTO 9: Check-out de Huésped (Libera y pasa a Limpieza)
CREATE OR REPLACE PROCEDURE public.sp_checkout_reserva(
    IN p_cod_reserva VARCHAR(6)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_num_hab VARCHAR(4);
BEGIN
    SELECT num_habitacion INTO v_num_hab
    FROM public."Habitacion"
    WHERE cod_reserva = p_cod_reserva;

    IF v_num_hab IS NULL THEN
        RAISE EXCEPTION 'La reserva % no tiene habitación asignada para check-out.', p_cod_reserva;
    END IF;

    UPDATE public."Habitacion"
    SET estado_habitacion = 'Limpieza',
        cod_reserva = NULL
    WHERE num_habitacion = v_num_hab;

    INSERT INTO public.auditoria_operaciones(tabla_afectada, operacion, registro_id, detalle)
    VALUES ('Habitacion', 'CHECKOUT', v_num_hab, 'Check-out procesado para reserva ' || p_cod_reserva || '. Habitación enviada a Limpieza.');
END;
$$;
