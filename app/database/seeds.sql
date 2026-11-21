-- ========================================================
-- HOTEL CUMBRE REAL AIRPORT - DATOS SEMILLA DE PRUEBA
-- 20 registros por tabla (200 registros totales)
-- ========================================================

BEGIN;

-- 1. TABLA: tipo_doc_identidad (20 registros)
INSERT INTO public.tipo_doc_identidad ("cod_tipoDoc", descripcion) VALUES
('D01', 'DNI'),
('D02', 'RUC'),
('D03', 'Carnet extranjeria'),
('D04', 'Pasaporte'),
('D05', 'PTP'),
('D06', 'CPP'),
('D07', 'Cedula identidad'),
('D08', 'DNI electronico'),
('D09', 'Doc diplomatico'),
('D10', 'Doc consular'),
('D11', 'Salvoconducto'),
('D12', 'Residencia'),
('D13', 'Doc provisional'),
('D14', 'Doc extranjero'),
('D15', 'Identidad militar'),
('D16', 'Identidad policial'),
('D17', 'Doc institucional'),
('D18', 'Doc especial'),
('D19', 'Doc temporal'),
('D20', 'Otro documento')
ON CONFLICT DO NOTHING;

-- 2. TABLA: tipo_habitacion (20 registros)
INSERT INTO public.tipo_habitacion ("cod_tipoHabitacion", descripcion, precio_habitacion) VALUES
('H01', 'Simple', 100.00),
('H02', 'Doble', 150.00),
('H03', 'Matrimonial', 180.00),
('H04', 'Triple', 220.00),
('H05', 'Familiar', 280.00),
('H06', 'Suite', 350.00),
('H07', 'Suite Junior', 300.00),
('H08', 'Suite Deluxe', 450.00),
('H09', 'Ejecutiva', 250.00),
('H10', 'Economica', 80.00),
('H11', 'Premium', 400.00),
('H12', 'Individual', 90.00),
('H13', 'Twin', 160.00),
('H14', 'King', 230.00),
('H15', 'Queen', 210.00),
('H16', 'Suite Familiar', 500.00),
('H17', 'Accesible', 140.00),
('H18', 'Presidencial', 900.00),
('H19', 'Business', 270.00),
('H20', 'Vista Exterior', 190.00)
ON CONFLICT DO NOTHING;

-- 3. TABLA: metodo_pago (20 registros)
INSERT INTO public.metodo_pago ("cod_metodoPago", descripcion) VALUES
('MP01', 'Efectivo'),
('MP02', 'Visa'),
('MP03', 'Mastercard'),
('MP04', 'Yape'),
('MP05', 'Plin'),
('MP06', 'Transferencia'),
('MP07', 'Deposito'),
('MP08', 'American Express'),
('MP09', 'Diners Club'),
('MP10', 'Tarjeta debito'),
('MP11', 'Tarjeta credito'),
('MP12', 'PayPal'),
('MP13', 'Pago QR'),
('MP14', 'Pago movil'),
('MP15', 'Cheque'),
('MP16', 'Pago web'),
('MP17', 'Pago empresa'),
('MP18', 'Pago adelantado'),
('MP19', 'Pago mixto'),
('MP20', 'Otro medio')
ON CONFLICT DO NOTHING;

-- 4. TABLA: medio_reserva (20 registros)
INSERT INTO public.medio_reserva ("cod_medioReserva", descripcion) VALUES
('M01', 'Presencial'),
('M02', 'Telefono'),
('M03', 'WhatsApp'),
('M04', 'Web hotel'),
('M05', 'Booking'),
('M06', 'Expedia'),
('M07', 'Agencia'),
('M08', 'Correo'),
('M09', 'Facebook'),
('M10', 'Instagram'),
('M11', 'Airbnb'),
('M12', 'Trivago'),
('M13', 'Empresa'),
('M14', 'Aplicacion'),
('M15', 'Google'),
('M16', 'Referido'),
('M17', 'Tour op.'),
('M18', 'Chat web'),
('M19', 'Otro canal'),
('M20', 'Convenio')
ON CONFLICT DO NOTHING;

-- 5. TABLA: Recepcionista (20 registros)
INSERT INTO public."Recepcionista" (cod_recepcionista, nombres, apellidos) VALUES
('E001', 'Ana', 'Torres Ramirez'),
('E002', 'Luis', 'Mendoza Flores'),
('E003', 'Maria', 'Quispe Huaman'),
('E004', 'Carlos', 'Rojas Vargas'),
('E005', 'Lucia', 'Flores Medina'),
('E006', 'Jorge', 'Castillo Perez'),
('E007', 'Elena', 'Vargas Soto'),
('E008', 'Miguel', 'Condori Mamani'),
('E009', 'Rosa', 'Chavez Paredes'),
('E010', 'Pedro', 'Gutierrez Leon'),
('E011', 'Carmen', 'Salas Rivera'),
('E012', 'Diego', 'Herrera Cruz'),
('E013', 'Patricia', 'Lopez Cardenas'),
('E014', 'Fernando', 'Aguilar Ramos'),
('E015', 'Andrea', 'Romero Silva'),
('E016', 'Ricardo', 'Paredes Diaz'),
('E017', 'Sofia', 'Medina Torres'),
('E018', 'Alberto', 'Navarro Ruiz'),
('E019', 'Valeria', 'Sanchez Ortiz'),
('E020', 'Martin', 'Reyes Flores')
ON CONFLICT DO NOTHING;

-- 6. TABLA: Huesped (20 registros)
INSERT INTO public."Huesped" (doc_identidad, "cod_tipoDoc", nombres, apellidos, correo) VALUES
('DOC00000001', 'D01', 'Juan', 'Perez Lopez', 'juan.perez@example.com'),
('DOC00000002', 'D02', 'Maria', 'Garcia Torres', 'maria.garcia@example.com'),
('DOC00000003', 'D03', 'Carlos', 'Quispe Flores', 'carlos.quispe@example.com'),
('DOC00000004', 'D04', 'Ana', 'Rodriguez Diaz', 'ana.rodriguez@example.com'),
('DOC00000005', 'D05', 'Luis', 'Mendoza Rojas', 'luis.mendoza@example.com'),
('DOC00000006', 'D06', 'Rosa', 'Huaman Soto', 'rosa.huaman@example.com'),
('DOC00000007', 'D07', 'Pedro', 'Castillo Vega', 'pedro.castillo@example.com'),
('DOC00000008', 'D08', 'Lucia', 'Vargas Medina', 'lucia.vargas@example.com'),
('DOC00000009', 'D09', 'Jorge', 'Ramos Salas', 'jorge.ramos@example.com'),
('DOC00000010', 'D10', 'Elena', 'Chavez Ruiz', 'elena.chavez@example.com'),
('DOC00000011', 'D11', 'Miguel', 'Flores Leon', 'miguel.flores@example.com'),
('DOC00000012', 'D12', 'Carmen', 'Sanchez Cruz', 'carmen.sanchez@example.com'),
('DOC00000013', 'D13', 'Diego', 'Romero Paredes', 'diego.romero@example.com'),
('DOC00000014', 'D14', 'Patricia', 'Aguilar Torres', 'patricia.aguilar@example.com'),
('DOC00000015', 'D15', 'Fernando', 'Navarro Diaz', 'fernando.navarro@example.com'),
('DOC00000016', 'D16', 'Andrea', 'Medina Vargas', 'andrea.medina@example.com'),
('DOC00000017', 'D17', 'Ricardo', 'Reyes Flores', 'ricardo.reyes@example.com'),
('DOC00000018', 'D18', 'Sofia', 'Herrera Soto', 'sofia.herrera@example.com'),
('DOC00000019', 'D19', 'Alberto', 'Ortiz Rojas', 'alberto.ortiz@example.com'),
('DOC00000020', 'D20', 'Valeria', 'Silva Mendoza', 'valeria.silva@example.com')
ON CONFLICT DO NOTHING;

-- 7. TABLA: Reserva (20 registros)
INSERT INTO public."Reserva"
(cod_reserva, fecha_reserva, hora_reserva, fecha_hora_ingreso, fecha_hora_salida, "cod_medioReserva", observaciones, solicita_desayuno, doc_identidad, cod_recepcionista) VALUES
('R00001', '2026-10-01', '08:30', '2026-10-31 14:00:00', '2026-11-01 11:00:00', 'M01', 'Llegada por la manana', TRUE, 'DOC00000001', 'E001'),
('R00002', '2026-10-02', '09:15', '2026-11-01 15:00:00', '2026-11-02 12:00:00', 'M02', 'Solicita habitacion tranquila', FALSE, 'DOC00000002', 'E002'),
('R00003', '2026-10-03', '10:00', '2026-11-02 14:30:00', '2026-11-03 10:00:00', 'M03', 'Llegada en taxi', TRUE, 'DOC00000003', 'E003'),
('R00004', '2026-10-04', '11:20', '2026-11-03 15:00:00', '2026-11-04 11:00:00', 'M04', 'Vista exterior', TRUE, 'DOC00000004', 'E004'),
('R00005', '2026-10-05', '12:00', '2026-11-04 14:00:00', '2026-11-05 12:00:00', 'M05', 'Reserva confirmada', FALSE, 'DOC00000005', 'E005'),
('R00006', '2026-10-06', '13:10', '2026-11-05 15:30:00', '2026-11-06 10:00:00', 'M06', 'Viaje de negocios', TRUE, 'DOC00000006', 'E006'),
('R00007', '2026-10-07', '14:30', '2026-11-06 14:00:00', '2026-11-07 11:00:00', 'M07', 'Estadia familiar', TRUE, 'DOC00000007', 'E007'),
('R00008', '2026-10-08', '15:00', '2026-11-07 15:00:00', '2026-11-08 12:00:00', 'M08', 'Solicita factura', FALSE, 'DOC00000008', 'E008'),
('R00009', '2026-10-09', '16:45', '2026-11-08 22:00:00', '2026-11-09 10:00:00', 'M09', 'Llegada nocturna', TRUE, 'DOC00000009', 'E009'),
('R00010', '2026-10-10', '17:15', '2026-11-09 16:00:00', '2026-11-10 11:00:00', 'M10', 'Estadia corta', FALSE, 'DOC00000010', 'E010'),
('R00011', '2026-10-11', '08:00', '2026-11-10 14:00:00', '2026-11-11 12:00:00', 'M11', 'Viaje turistico', TRUE, 'DOC00000011', 'E011'),
('R00012', '2026-10-12', '09:40', '2026-11-11 15:00:00', '2026-11-12 10:00:00', 'M12', 'Habitacion accesible', TRUE, 'DOC00000012', 'E012'),
('R00013', '2026-10-13', '10:25', '2026-11-12 14:30:00', '2026-11-13 11:00:00', 'M13', 'Reserva corporativa', FALSE, 'DOC00000013', 'E013'),
('R00014', '2026-10-14', '11:50', '2026-11-13 15:00:00', '2026-11-14 12:00:00', 'M14', 'Viaje personal', TRUE, 'DOC00000014', 'E014'),
('R00015', '2026-10-15', '12:35', '2026-11-14 14:00:00', '2026-11-15 10:00:00', 'M15', 'Confirmacion web', FALSE, 'DOC00000015', 'E015'),
('R00016', '2026-10-16', '13:45', '2026-11-15 15:30:00', '2026-11-16 11:00:00', 'M16', 'Cliente referido', TRUE, 'DOC00000016', 'E016'),
('R00017', '2026-10-17', '14:10', '2026-11-16 14:00:00', '2026-11-17 12:00:00', 'M17', 'Grupo turistico', TRUE, 'DOC00000017', 'E017'),
('R00018', '2026-10-18', '15:30', '2026-11-17 15:00:00', '2026-11-18 10:00:00', 'M18', 'Consulta por chat', FALSE, 'DOC00000018', 'E018'),
('R00019', '2026-10-19', '16:20', '2026-11-18 14:30:00', '2026-11-19 11:00:00', 'M19', 'Solicitud especial', TRUE, 'DOC00000019', 'E019'),
('R00020', '2026-10-20', '17:40', '2026-11-19 15:00:00', '2026-11-20 12:00:00', 'M20', 'Reserva por convenio', FALSE, 'DOC00000020', 'E020')
ON CONFLICT DO NOTHING;

-- 8. TABLA: Habitacion (20 registros)
INSERT INTO public."Habitacion" (num_habitacion, "cod_tipoHabitacion", estado_habitacion, cod_reserva) VALUES
('0101', 'H01', 'Disponible', NULL),
('0102', 'H02', 'Reservada', 'R00002'),
('0103', 'H03', 'Ocupada', 'R00003'),
('0104', 'H04', 'Limpieza', NULL),
('0105', 'H05', 'Mantenimiento', NULL),
('0106', 'H06', 'Disponible', NULL),
('0107', 'H07', 'Reservada', 'R00007'),
('0108', 'H08', 'Ocupada', 'R00008'),
('0109', 'H09', 'Disponible', NULL),
('0110', 'H10', 'Limpieza', NULL),
('0201', 'H11', 'Reservada', 'R00011'),
('0202', 'H12', 'Ocupada', 'R00012'),
('0203', 'H13', 'Disponible', NULL),
('0204', 'H14', 'Reservada', 'R00014'),
('0205', 'H15', 'Limpieza', NULL),
('0206', 'H16', 'Ocupada', 'R00016'),
('0207', 'H17', 'Disponible', NULL),
('0208', 'H18', 'Mantenimiento', NULL),
('0209', 'H19', 'Reservada', 'R00019'),
('0210', 'H20', 'Ocupada', 'R00020')
ON CONFLICT DO NOTHING;

-- 9. TABLA: Pago (20 registros)
INSERT INTO public."Pago" (cod_pago, monto_pago, "cod_metodoPago", cod_reserva, cod_recepcionista) VALUES
('P00001', 100.00, 'MP01', 'R00001', 'E001'),
('P00002', 150.00, 'MP02', 'R00002', 'E002'),
('P00003', 180.00, 'MP03', 'R00003', 'E003'),
('P00004', 220.00, 'MP04', 'R00004', 'E004'),
('P00005', 280.00, 'MP05', 'R00005', 'E005'),
('P00006', 350.00, 'MP06', 'R00006', 'E006'),
('P00007', 300.00, 'MP07', 'R00007', 'E007'),
('P00008', 450.00, 'MP08', 'R00008', 'E008'),
('P00009', 250.00, 'MP09', 'R00009', 'E009'),
('P00010', 80.00, 'MP10', 'R00010', 'E010'),
('P00011', 400.00, 'MP11', 'R00011', 'E011'),
('P00012', 90.00, 'MP12', 'R00012', 'E012'),
('P00013', 160.00, 'MP13', 'R00013', 'E013'),
('P00014', 230.00, 'MP14', 'R00014', 'E014'),
('P00015', 210.00, 'MP15', 'R00015', 'E015'),
('P00016', 500.00, 'MP16', 'R00016', 'E016'),
('P00017', 140.00, 'MP17', 'R00017', 'E017'),
('P00018', 900.00, 'MP18', 'R00018', 'E018'),
('P00019', 270.00, 'MP19', 'R00019', 'E019'),
('P00020', 190.00, 'MP20', 'R00020', 'E020')
ON CONFLICT DO NOTHING;

-- 10. TABLA: Telefono (20 registros)
INSERT INTO public."Telefono" (doc_identidad, num_telefono) VALUES
('DOC00000001', '900000001'),
('DOC00000002', '900000002'),
('DOC00000003', '900000003'),
('DOC00000004', '900000004'),
('DOC00000005', '900000005'),
('DOC00000006', '900000006'),
('DOC00000007', '900000007'),
('DOC00000008', '900000008'),
('DOC00000009', '900000009'),
('DOC00000010', '900000010'),
('DOC00000011', '900000011'),
('DOC00000012', '900000012'),
('DOC00000013', '900000013'),
('DOC00000014', '900000014'),
('DOC00000015', '900000015'),
('DOC00000016', '900000016'),
('DOC00000017', '900000017'),
('DOC00000018', '900000018'),
('DOC00000019', '900000019'),
('DOC00000020', '900000020')
ON CONFLICT DO NOTHING;

-- Sincronizar secuencias
SELECT setval(
    'public.recepcionista_codigo_seq',
    (SELECT COALESCE(MAX(SUBSTRING(cod_recepcionista FROM 2)::INTEGER), 1) FROM public."Recepcionista"),
    TRUE
);

SELECT setval(
    'public.reserva_codigo_seq',
    (SELECT COALESCE(MAX(SUBSTRING(cod_reserva FROM 2)::INTEGER), 1) FROM public."Reserva"),
    TRUE
);

SELECT setval(
    'public.pago_codigo_seq',
    (SELECT COALESCE(MAX(SUBSTRING(cod_pago FROM 2)::INTEGER), 1) FROM public."Pago"),
    TRUE
);

COMMIT;
