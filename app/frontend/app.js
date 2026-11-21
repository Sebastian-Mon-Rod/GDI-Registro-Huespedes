/* ========================================================
   ALOJAGEST - SISTEMA INTEGRAL DE GESTIÓN HOTELERA
   Lógica de Aplicación (Vanilla JS - Cero Frameworks)
   ======================================================== */

// Estado reactivo global de AlojaGest
const state = {
  session: null, // { cod_recepcionista, nombres, apellidos, rol, usuario, dni }
  dashboard: {},
  reservas: [],
  huespedes: [],
  habitaciones: [],
  habitacionesDisponibles: [],
  catalogos: {},
  empleados: [],
  recepcionistaActivo: "E001",
  filtroRack: "todos",
  modoEdicionReserva: false,
  modoEdicionHuesped: false,
  modoEdicionEmpleado: false,
  reporteActivo: 1
};

// Inicialización
document.addEventListener("DOMContentLoaded", () => {
  initClock();
  initSidebar();
  initAuthSession();
  initNavTabs();
  initEventHandlers();
  loadCatalogos();
  checkHealth();
  recargarDashboard();
  loadReservas();
  loadHabitaciones();
  loadHuespedes();
  loadAuditoria();
  cargarReporte(1); // Cargar primer reporte corporativo por defecto

  // Auto-refresh suave de métricas cada 45s
  setInterval(() => {
    recargarDashboard();
  }, 45000);
});

/* ========================================================
   RELOJ Y FECHA EN TIEMPO REAL
   ======================================================== */
function initClock() {
  const clockEl = document.getElementById("live-clock");
  const dateEl = document.getElementById("live-date");

  function tick() {
    const now = new Date();
    if (clockEl) clockEl.textContent = now.toLocaleTimeString("es-PE", { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    if (dateEl) dateEl.textContent = now.toLocaleDateString("es-PE", { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' });
  }
  tick();
  setInterval(tick, 1000);
}

/* ========================================================
   MENÚ LATERAL IZQUIERDO (SIDEBAR DESPLEGABLE / COLAPSABLE)
   ======================================================== */
function initSidebar() {
  const sidebar = document.getElementById("app-sidebar");
  const toggleBtn = document.getElementById("btn-toggle-sidebar");
  const mobileToggleBtn = document.getElementById("btn-sidebar-mobile-toggle");

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
    });
  }

  if (mobileToggleBtn && sidebar) {
    mobileToggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("mobile-open");
    });
  }
}

/* ========================================================
   AUTENTICACIÓN Y SESIÓN (LOGIN CORPORATIVO)
   ======================================================== */
function initAuthSession() {
  const overlay = document.getElementById("login-overlay");
  const formLogin = document.getElementById("form-login");
  const btnLogout = document.getElementById("btn-logout");
  const alertBox = document.getElementById("login-alert");

  const stored = localStorage.getItem("alojagest_session");
  if (stored) {
    try {
      state.session = JSON.parse(stored);
      state.recepcionistaActivo = state.session.cod_recepcionista;
      aplicarSesionUI();
      if (overlay) overlay.classList.add("hidden");
    } catch (e) {
      localStorage.removeItem("alojagest_session");
      if (overlay) overlay.classList.remove("hidden");
    }
  } else {
    if (overlay) overlay.classList.remove("hidden");
  }

  if (formLogin) {
    formLogin.addEventListener("submit", async (e) => {
      e.preventDefault();
      const usuario = document.getElementById("login-usuario").value.trim();
      const password = document.getElementById("login-password").value.trim();
      const submitBtn = document.getElementById("btn-login-submit");

      if (alertBox) alertBox.style.display = "none";
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Verificando...";
      }

      try {
        const res = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ usuario, password })
        });
        const json = await res.json();

        if (json.success && json.data) {
          state.session = json.data;
          state.recepcionistaActivo = json.data.cod_recepcionista;
          localStorage.setItem("alojagest_session", JSON.stringify(json.data));
          aplicarSesionUI();
          if (overlay) overlay.classList.add("hidden");
          showToast(`¡Bienvenido(a), ${json.data.nombres}!`, "success");
        } else {
          if (alertBox) {
            alertBox.textContent = json.error || "Credenciales incorrectas.";
            alertBox.style.display = "block";
          }
        }
      } catch (err) {
        if (alertBox) {
          alertBox.textContent = `Error al conectar: ${err.message}`;
          alertBox.style.display = "block";
        }
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = "Ingresar al Sistema";
        }
      }
    });
  }

  if (btnLogout) {
    btnLogout.addEventListener("click", () => {
      localStorage.removeItem("alojagest_session");
      state.session = null;
      if (overlay) {
        overlay.classList.remove("hidden");
        const uInput = document.getElementById("login-usuario");
        const pInput = document.getElementById("login-password");
        if (uInput) uInput.value = "";
        if (pInput) pInput.value = "";
      }
      showToast("Sesión finalizada.", "info");
    });
  }
}

function aplicarSesionUI() {
  if (!state.session) return;
  const user = state.session;

  const nameEl = document.getElementById("sidebar-user-name");
  const roleEl = document.getElementById("sidebar-user-role");
  const avatarEl = document.getElementById("sidebar-user-avatar");
  const adminItems = document.querySelectorAll(".nav-admin-only");

  if (nameEl) nameEl.textContent = `${user.nombres} ${user.apellidos}`;
  if (roleEl) {
    roleEl.textContent = user.rol;
    roleEl.className = `user-role badge ${user.rol === 'Administrador' ? 'badge-admin' : 'badge-secondary'}`;
  }
  if (avatarEl) {
    avatarEl.textContent = user.rol === "Administrador" ? "👑" : "👤";
  }

  // Control de Acceso Basado en Roles (RBAC)
  if (user.rol === "Administrador") {
    adminItems.forEach(el => el.style.display = "flex");
  } else {
    adminItems.forEach(el => el.style.display = "none");
    const activeTab = document.querySelector(".sidebar-nav-item.active");
    if (activeTab && activeTab.getAttribute("data-tab") === "tab-empleados") {
      cambiarPestana("tab-dashboard");
    }
  }
}

/* ========================================================
   NAVEGACIÓN POR PESTAÑAS (TABS)
   ======================================================== */
function initNavTabs() {
  const tabBtns = document.querySelectorAll(".sidebar-nav-item, .nav-tab-btn");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");
      cambiarPestana(targetId);
      const sidebar = document.getElementById("app-sidebar");
      if (sidebar && window.innerWidth <= 900) {
        sidebar.classList.remove("mobile-open");
      }
    });
  });
}

function cambiarPestana(tabId) {
  const tabBtns = document.querySelectorAll(".sidebar-nav-item, .nav-tab-btn");
  const panes = document.querySelectorAll(".module-tab, .tab-pane");

  tabBtns.forEach(b => b.classList.remove("active"));
  panes.forEach(p => p.classList.remove("active"));

  const targetBtns = document.querySelectorAll(`[data-tab="${tabId}"]`);
  const targetPane = document.getElementById(tabId);

  targetBtns.forEach(b => b.classList.add("active"));
  if (targetPane) targetPane.classList.add("active");

  // Acciones bajo demanda
  if (tabId === "tab-dashboard") recargarDashboard();
  if (tabId === "tab-rack") loadHabitaciones();
  if (tabId === "tab-reservas") loadReservas();
  if (tabId === "tab-huespedes") loadHuespedes();
  if (tabId === "tab-auditoria") loadAuditoria();
  if (tabId === "tab-empleados") loadEmpleados();
}

window.cambiarPestana = cambiarPestana;

function navegarARack(estadoFiltro) {
  cambiarPestana("tab-rack");
  filtrarRackPorEstado(estadoFiltro);
}
window.navegarARack = navegarARack;

/* ========================================================
   EVENT HANDLERS Y MODALES
   ======================================================== */
function initEventHandlers() {
  // Recepcionista activo si existe selector legado
  const selectRecep = document.getElementById("select-active-receptionist");
  if (selectRecep) {
    selectRecep.addEventListener("change", (e) => {
      state.recepcionistaActivo = e.target.value;
      showToast(`Operador activo: ${selectRecep.options[selectRecep.selectedIndex].text}`, "info");
    });
  }

  // Botones de acción rápida en topbar
  const btnNuevaReserva = document.getElementById("btn-nueva-reserva-quick");
  if (btnNuevaReserva) btnNuevaReserva.addEventListener("click", () => abrirModalReserva(false));

  const btnNuevoHuesped = document.getElementById("btn-nuevo-huesped-quick");
  if (btnNuevoHuesped) btnNuevoHuesped.addEventListener("click", () => abrirModalHuesped(false));

  // Filtros de búsqueda en Reservas
  const searchReservas = document.getElementById("input-search-reservas");
  if (searchReservas) searchReservas.addEventListener("input", filtrarReservas);

  const filterReservaEstado = document.getElementById("filter-reserva-estado");
  if (filterReservaEstado) filterReservaEstado.addEventListener("change", filtrarReservas);

  // Filtros de búsqueda en Huéspedes
  const searchHuespedes = document.getElementById("input-search-huespedes");
  if (searchHuespedes) {
    searchHuespedes.addEventListener("input", (e) => {
      filtrarHuespedes(e.target.value.toLowerCase().trim());
    });
  }

  // Filtros del Rack de habitaciones
  const rackFilterBtns = document.querySelectorAll(".filter-rack-btn");
  rackFilterBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      rackFilterBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      filtrarRackPorEstado(btn.getAttribute("data-filter"));
    });
  });

  // Cierre de modales
  setupModalClose("modal-reserva", "btn-close-modal-reserva", "btn-cancel-modal-reserva");
  setupModalClose("modal-huesped", "btn-close-modal-huesped", "btn-cancel-modal-huesped");
  setupModalClose("modal-voucher", "btn-close-modal-voucher", "btn-cancel-modal-voucher");
  setupModalClose("modal-empleado", "btn-close-modal-empleado", "btn-cancel-modal-empleado");

  // Formularios
  const formReserva = document.getElementById("form-reserva");
  if (formReserva) {
    formReserva.addEventListener("submit", async (e) => {
      e.preventDefault();
      await guardarReserva();
    });
  }

  const formHuesped = document.getElementById("form-huesped");
  if (formHuesped) {
    formHuesped.addEventListener("submit", async (e) => {
      e.preventDefault();
      await guardarHuesped();
    });
  }

  const formEmpleado = document.getElementById("form-empleado");
  if (formEmpleado) {
    formEmpleado.addEventListener("submit", async (e) => {
      e.preventDefault();
      await guardarEmpleado();
    });
  }
}

function setupModalClose(modalId, closeBtnId, cancelBtnId) {
  const modal = document.getElementById(modalId);
  const closeBtn = document.getElementById(closeBtnId);
  const cancelBtn = document.getElementById(cancelBtnId);

  const close = () => modal.classList.remove("open");
  if (closeBtn) closeBtn.addEventListener("click", close);
  if (cancelBtn) cancelBtn.addEventListener("click", close);
}

/* ========================================================
   DIAGNÓSTICO Y CONEXIÓN A POSTGRESQL
   ======================================================== */
async function checkHealth() {
  const badge = document.getElementById("db-status-badge");
  const text = document.getElementById("db-status-text");

  try {
    const res = await fetch("/api/health");
    const json = await res.json();

    if (json.success && json.data.status === "connected") {
      const d = json.data;
      badge.className = "badge badge-success";
      text.textContent = `PostgreSQL Online (${d.latency_ms} ms)`;

      const cfgLatency = document.getElementById("cfg-latency");
      if (cfgLatency) cfgLatency.textContent = `${d.latency_ms} ms`;
      const cfgVer = document.getElementById("cfg-version");
      if (cfgVer) cfgVer.textContent = d.version.split(",")[0];
      const cfgCount = document.getElementById("cfg-table-count");
      if (cfgCount) cfgCount.textContent = d.table_count;

      const listContainer = document.getElementById("cfg-tables-list");
      if (listContainer) {
        listContainer.innerHTML = d.tables.map(t => `<span class="tag">dbo.${t}</span>`).join("");
      }
    } else {
      throw new Error(json.data ? json.data.error : "Fallo de conexión");
    }
  } catch (err) {
    badge.className = "badge badge-danger";
    text.textContent = "Base de Datos Offline";
    showToast(`Error al conectar con PostgreSQL: ${err.message}`, "error");
  }
}

/* ========================================================
   PANEL EJECUTIVO (DASHBOARD)
   ======================================================== */
async function recargarDashboard() {
  try {
    const res = await fetch("/api/dashboard");
    const json = await res.json();
    if (json.success) {
      const d = json.data;
      state.dashboard = d;

      document.getElementById("kpi-ocupacion").textContent = `${d.tasa_ocupacion}%`;
      document.getElementById("kpi-ocupadas-ratio").textContent = d.hab_ocupadas;
      document.getElementById("kpi-libres").textContent = d.hab_disponibles;
      document.getElementById("kpi-reservadas").textContent = d.hab_reservadas;
      document.getElementById("kpi-limpieza").textContent = d.hab_limpieza;
      document.getElementById("kpi-huespedes").textContent = d.total_huespedes;

      document.getElementById("stat-llegadas-hoy").textContent = d.llegadas_hoy;
      document.getElementById("stat-salidas-hoy").textContent = d.salidas_hoy;

      // Actualizar gráfica de barras de distribución
      const total = d.total_habitaciones || 20;
      const pctOcup = (d.hab_ocupadas / total) * 100;
      const pctRes = (d.hab_reservadas / total) * 100;
      const pctDisp = (d.hab_disponibles / total) * 100;
      const pctLimp = (d.hab_limpieza / total) * 100;

      document.getElementById("bar-ocupadas").style.width = `${pctOcup}%`;
      document.getElementById("bar-reservadas").style.width = `${pctRes}%`;
      document.getElementById("bar-disponibles").style.width = `${pctDisp}%`;
      document.getElementById("bar-limpieza").style.width = `${pctLimp}%`;

      document.getElementById("leg-disp").textContent = d.hab_disponibles;
      document.getElementById("leg-res").textContent = d.hab_reservadas;
      document.getElementById("leg-ocup").textContent = d.hab_ocupadas;
      document.getElementById("leg-limp").textContent = d.hab_limpieza;
    }
  } catch (e) {
    console.error("Error al cargar dashboard:", e);
  }
}
window.recargarDashboard = recargarDashboard;

/* ========================================================
   CATÁLOGOS
   ======================================================== */
async function loadCatalogos() {
  try {
    const res = await fetch("/api/catalogos");
    const json = await res.json();
    if (json.success) {
      state.catalogos = json.data;

      // Poblar selector de recepcionistas si existe
      const selectRecep = document.getElementById("select-active-receptionist");
      if (selectRecep) {
        selectRecep.innerHTML = state.catalogos.recepcionistas.map(r => 
          `<option value="${r.cod_recepcionista}">${r.nombres} ${r.apellidos} (${r.cod_recepcionista})</option>`
        ).join("");
        if (!state.session) {
          state.recepcionistaActivo = selectRecep.value;
        }
      }

      // Poblar tipos de documento
      const selectTipoDoc = document.getElementById("input-huesped-tipodoc");
      if (selectTipoDoc) {
        selectTipoDoc.innerHTML = state.catalogos.tipos_documento.map(t => 
          `<option value="${t.cod_tipoDoc}">${t.descripcion} (${t.cod_tipoDoc})</option>`
        ).join("");
      }

      // Poblar canales de reserva
      const selectMedio = document.getElementById("select-reserva-medio");
      if (selectMedio) {
        selectMedio.innerHTML = state.catalogos.medios_reserva.map(m => 
          `<option value="${m.cod_medioReserva}">${m.descripcion}</option>`
        ).join("");
      }
    }
  } catch (e) {
    console.error("Error al cargar catálogos:", e);
  }
}

/* ========================================================
   RACK INTERACTIVO DE HABITACIONES
   ======================================================== */
async function loadHabitaciones() {
  const container = document.getElementById("rack-container");
  try {
    const res = await fetch("/api/habitaciones");
    const json = await res.json();

    if (json.success) {
      state.habitaciones = json.data;
      renderRackHabitaciones();
    }
  } catch (e) {
    console.error("Error al cargar habitaciones:", e);
  }
}

function filtrarRackPorEstado(estado) {
  state.filtroRack = estado;
  renderRackHabitaciones();
}

function renderRackHabitaciones() {
  const container = document.getElementById("rack-container");
  let lista = state.habitaciones;

  if (state.filtroRack !== "todos") {
    lista = lista.filter(h => h.estado_habitacion === state.filtroRack);
  }

  container.innerHTML = lista.map(h => {
    const estadoClass = h.estado_habitacion.toLowerCase();
    const precio = parseFloat(h.precio_habitacion).toFixed(2);
    
    let infoOcupacion = "";
    let botonAccion = "";

    if (h.estado_habitacion === "Disponible") {
      botonAccion = `<button class="btn btn-primary btn-sm" onclick="reservarHabitacionDirecta('${h.num_habitacion}')">➕ Reservar</button>`;
    } else if (h.estado_habitacion === "Limpieza") {
      botonAccion = `<button class="btn btn-success btn-sm" onclick="marcarHabitacionLimpia('${h.num_habitacion}')">🧹 Marcar Limpia</button>`;
    } else if (h.estado_habitacion === "Reservada") {
      infoOcupacion = `
        <div class="room-guest-info">
          📋 Reserva: <b>${h.cod_reserva}</b><br>
          👤 ${escapeHtml(h.huesped_asignado || 'Titular')}
        </div>
      `;
      botonAccion = `<button class="btn btn-success btn-sm" onclick="checkinReserva('${h.cod_reserva}')">🛎️ Check-in</button>`;
    } else if (h.estado_habitacion === "Ocupada") {
      infoOcupacion = `
        <div class="room-guest-info">
          🔑 En Hospedaje:<br>
          <b>${escapeHtml(h.huesped_asignado || 'Huésped')}</b>
        </div>
      `;
      botonAccion = `<button class="btn btn-warning btn-sm" onclick="checkoutReserva('${h.cod_reserva}')">🚪 Check-out</button>`;
    }

    return `
      <div class="room-card ${estadoClass}">
        <div>
          <div class="room-header">
            <span class="room-number">Hab. ${escapeHtml(h.num_habitacion)}</span>
            <span class="badge ${getBadgeClass(h.estado_habitacion)}">${escapeHtml(h.estado_habitacion)}</span>
          </div>
          <div class="room-type">${escapeHtml(h.tipo_habitacion)}</div>
          <div class="room-price">S/ ${precio} <small class="text-muted">/ noche</small></div>
          ${infoOcupacion}
        </div>
        <div class="room-card-actions">
          ${botonAccion}
        </div>
      </div>
    `;
  }).join("");
}

window.reservarHabitacionDirecta = function(numHab) {
  abrirModalReserva(false, null, numHab);
};

window.marcarHabitacionLimpia = async function(numHab) {
  try {
    const res = await fetch("/api/habitaciones/estado", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ num_habitacion: numHab, nuevo_estado: "Disponible" })
    });
    const json = await res.json();
    if (json.success) {
      showToast(json.message, "success");
      loadHabitaciones();
      recargarDashboard();
      loadAuditoria();
    } else {
      showToast(`Error: ${json.error}`, "error");
    }
  } catch (err) {
    showToast(`Error de red: ${err.message}`, "error");
  }
};

/* ========================================================
   GESTIÓN DE RESERVAS Y ESTADÍAS
   ======================================================== */
async function loadReservas() {
  const tbody = document.getElementById("tbody-reservas");
  try {
    const res = await fetch("/api/reservas");
    const json = await res.json();

    if (json.success) {
      state.reservas = json.data;
      filtrarReservas();
    }
  } catch (err) {
    if (tbody) tbody.innerHTML = `<tr><td colspan="9" class="loading-td" style="color:var(--status-ocupada)">Error: ${err.message}</td></tr>`;
  }
}

function renderReservas(lista) {
  const tbody = document.getElementById("tbody-reservas");
  const badge = document.getElementById("reservas-count-badge");
  badge.textContent = `${lista.length} de ${state.reservas.length} registradas`;

  if (lista.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="loading-td">No se encontraron reservas con los criterios actuales.</td></tr>`;
    return;
  }

  tbody.innerHTML = lista.map(r => {
    const cod = escapeHtml(r.cod_reserva);
    const huesped = escapeHtml(r.huesped_nombre || "Sin huésped");
    const doc = escapeHtml(r.doc_identidad);
    const habNum = r.num_habitacion ? `<b>Hab. ${escapeHtml(r.num_habitacion)}</b> <small>(${escapeHtml(r.tipo_habitacion || '')})</small>` : `<span class="badge badge-secondary">Sin asignar</span>`;
    const fIngreso = formatDateTime(r.fecha_hora_ingreso);
    const fSalida = formatDateTime(r.fecha_hora_salida);
    const canal = escapeHtml(r.medio_reserva_desc || r.cod_medioReserva);
    const desayuno = r.solicita_desayuno ? `<span class="badge badge-success">🍳 Sí</span>` : `<span class="badge badge-secondary">No</span>`;
    const estadoHab = r.estado_habitacion || "Disponible";
    const estadoBadge = getBadgeClass(estadoHab);

    let botones = "";
    if (estadoHab === "Reservada") {
      botones += `<button class="btn btn-success btn-sm" onclick="checkinReserva('${cod}')" title="Registrar llegada">🛎️ In</button> `;
    } else if (estadoHab === "Ocupada") {
      botones += `<button class="btn btn-warning btn-sm" onclick="checkoutReserva('${cod}')" title="Registrar salida">🚪 Out</button> `;
    }

    botones += `
      <button class="btn btn-secondary btn-sm" onclick="verVoucherReserva('${cod}')" title="Ver Voucher">📄</button>
      <button class="btn btn-secondary btn-sm" onclick="editarReserva('${cod}')" title="Modificar">✏️</button>
      <button class="btn btn-danger btn-sm" onclick="cancelarReserva('${cod}')" title="Cancelar">❌</button>
    `;

    return `
      <tr>
        <td><b>${cod}</b></td>
        <td>
          <b>${huesped}</b><br>
          <small class="text-muted">Doc: ${doc}</small>
        </td>
        <td>${habNum}</td>
        <td>${fIngreso}</td>
        <td>${fSalida}</td>
        <td><span class="badge badge-secondary">${canal}</span></td>
        <td>${desayuno}</td>
        <td><span class="badge ${estadoBadge}">${estadoHab}</span></td>
        <td style="text-align: center;">
          <div class="table-actions">${botones}</div>
        </td>
      </tr>
    `;
  }).join("");
}

function filtrarReservas() {
  const termino = document.getElementById("input-search-reservas").value.trim().toLowerCase();
  const estado = document.getElementById("filter-reserva-estado").value;

  const filtradas = state.reservas.filter(r => {
    const matchTerm = !termino || 
      r.cod_reserva.toLowerCase().includes(termino) ||
      (r.huesped_nombre && r.huesped_nombre.toLowerCase().includes(termino)) ||
      r.doc_identidad.toLowerCase().includes(termino) ||
      (r.num_habitacion && r.num_habitacion.includes(termino));

    const matchEstado = (estado === "todos") || (r.estado_habitacion === estado);
    return matchTerm && matchEstado;
  });

  renderReservas(filtradas);
}

// Check-in vía Stored Procedure
window.checkinReserva = async function(codReserva) {
  if (!confirm(`¿Confirmar Check-in para la reserva ${codReserva}?\nLa habitación pasará a estado 'Ocupada'.`)) return;

  try {
    const res = await fetch("/api/reservas/checkin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cod_reserva: codReserva })
    });
    const json = await res.json();
    if (json.success) {
      showToast(json.message, "success");
      loadReservas();
      loadHabitaciones();
      recargarDashboard();
      loadAuditoria();
    } else {
      showToast(`Error: ${json.error}`, "error");
    }
  } catch (err) {
    showToast(`Error de conexión: ${err.message}`, "error");
  }
};

// Check-out vía Stored Procedure
window.checkoutReserva = async function(codReserva) {
  if (!confirm(`¿Confirmar Check-out para la reserva ${codReserva}?\nLa habitación será liberada y transferida a 'Limpieza'.`)) return;

  try {
    const res = await fetch("/api/reservas/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cod_reserva: codReserva })
    });
    const json = await res.json();
    if (json.success) {
      showToast(json.message, "success");
      loadReservas();
      loadHabitaciones();
      recargarDashboard();
      loadAuditoria();
    } else {
      showToast(`Error: ${json.error}`, "error");
    }
  } catch (err) {
    showToast(`Error de conexión: ${err.message}`, "error");
  }
};

// Cancelar Reserva vía Stored Procedure
window.cancelarReserva = async function(codReserva) {
  if (!confirm(`¿Está seguro de CANCELAR la reserva ${codReserva}?\nSe liberará la habitación y se registrará en auditoría.`)) return;

  try {
    const res = await fetch(`/api/reservas?cod_reserva=${encodeURIComponent(codReserva)}`, {
      method: "DELETE"
    });
    const json = await res.json();
    if (json.success) {
      showToast(json.message, "success");
      loadReservas();
      loadHabitaciones();
      recargarDashboard();
      loadAuditoria();
    } else {
      showToast(`Error al cancelar: ${json.error}`, "error");
    }
  } catch (err) {
    showToast(`Error de red: ${err.message}`, "error");
  }
};

// Modal de Creación / Edición de Reserva
async function abrirModalReserva(esEdicion, data = null, habPreseleccionada = null) {
  state.modoEdicionReserva = esEdicion;
  const modal = document.getElementById("modal-reserva");
  const modalTitle = document.getElementById("modal-reserva-title");
  const inputCod = document.getElementById("input-reserva-codigo");
  const selectHuesped = document.getElementById("select-reserva-huesped");
  const selectHab = document.getElementById("select-reserva-habitacion");
  const selectMedio = document.getElementById("select-reserva-medio");
  const inputIngreso = document.getElementById("input-reserva-ingreso");
  const inputSalida = document.getElementById("input-reserva-salida");
  const checkDesayuno = document.getElementById("input-reserva-desayuno");
  const inputObs = document.getElementById("input-reserva-obs");
  const alertBox = document.getElementById("reserva-alert");

  alertBox.style.display = "none";

  // Huéspedes
  await loadHuespedes();
  selectHuesped.innerHTML = state.huespedes.map(h => 
    `<option value="${h.doc_identidad}">${h.apellidos}, ${h.nombres} (${h.doc_identidad})</option>`
  ).join("");

  // Habitaciones Disponibles
  await loadHabitacionesDisponibles();
  let habOptions = state.habitacionesDisponibles.map(h => 
    `<option value="${h.num_habitacion}">Hab. ${h.num_habitacion} - ${h.tipo_habitacion} (S/ ${parseFloat(h.precio_habitacion).toFixed(2)})</option>`
  );

  if (esEdicion && data) {
    modalTitle.textContent = `Modificar Reserva ${data.cod_reserva}`;
    inputCod.value = data.cod_reserva;
    selectHuesped.value = data.doc_identidad;
    selectHuesped.disabled = true;

    if (data.num_habitacion) {
      if (!state.habitacionesDisponibles.some(h => h.num_habitacion === data.num_habitacion)) {
        habOptions.unshift(`<option value="${data.num_habitacion}" selected>Hab. ${data.num_habitacion} (Asignada Actualmente)</option>`);
      }
    }
    selectHab.innerHTML = habOptions.join("");
    selectHab.value = data.num_habitacion || "";

    selectMedio.value = data.cod_medioReserva;
    inputIngreso.value = toInputDateTime(data.fecha_hora_ingreso);
    inputSalida.value = toInputDateTime(data.fecha_hora_salida);
    checkDesayuno.checked = Boolean(data.solicita_desayuno);
    inputObs.value = data.observaciones || "";
  } else {
    modalTitle.textContent = "Registrar Nueva Reserva";
    inputCod.value = "";
    selectHuesped.disabled = false;
    selectHab.innerHTML = habOptions.join("");
    if (habPreseleccionada) selectHab.value = habPreseleccionada;

    const hoy = new Date();
    hoy.setHours(14, 0, 0, 0);
    const manana = new Date(hoy);
    manana.setDate(manana.getDate() + 1);
    manana.setHours(11, 0, 0, 0);

    inputIngreso.value = toInputDateTime(hoy);
    inputSalida.value = toInputDateTime(manana);
    checkDesayuno.checked = true;
    inputObs.value = "";
  }

  modal.classList.add("open");
}
window.abrirModalReserva = abrirModalReserva;

window.editarReserva = function(codReserva) {
  const r = state.reservas.find(x => x.cod_reserva === codReserva);
  if (r) abrirModalReserva(true, r);
};

async function loadHabitacionesDisponibles() {
  try {
    const res = await fetch("/api/habitaciones/disponibles");
    const json = await res.json();
    if (json.success) state.habitacionesDisponibles = json.data;
  } catch (e) {
    console.error("Error al cargar habitaciones disponibles:", e);
  }
}

async function guardarReserva() {
  const alertBox = document.getElementById("reserva-alert");
  const esEdicion = state.modoEdicionReserva;

  const payload = {
    cod_reserva: document.getElementById("input-reserva-codigo").value,
    doc_identidad: document.getElementById("select-reserva-huesped").value,
    num_habitacion: document.getElementById("select-reserva-habitacion").value,
    fecha_hora_ingreso: document.getElementById("input-reserva-ingreso").value.replace("T", " ") + ":00",
    fecha_hora_salida: document.getElementById("input-reserva-salida").value.replace("T", " ") + ":00",
    cod_medioReserva: document.getElementById("select-reserva-medio").value,
    cod_recepcionista: state.recepcionistaActivo,
    solicita_desayuno: document.getElementById("input-reserva-desayuno").checked,
    observaciones: document.getElementById("input-reserva-obs").value.trim()
  };

  if (new Date(payload.fecha_hora_salida) <= new Date(payload.fecha_hora_ingreso)) {
    alertBox.textContent = "La fecha y hora de salida debe ser posterior a la de ingreso.";
    alertBox.style.display = "block";
    return;
  }

  const method = esEdicion ? "PUT" : "POST";
  try {
    const res = await fetch("/api/reservas", {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const json = await res.json();

    if (json.success) {
      document.getElementById("modal-reserva").classList.remove("open");
      showToast(json.message, "success");
      loadReservas();
      loadHabitaciones();
      recargarDashboard();
      loadAuditoria();
    } else {
      alertBox.textContent = json.error;
      alertBox.style.display = "block";
    }
  } catch (err) {
    alertBox.textContent = `Error de comunicación: ${err.message}`;
    alertBox.style.display = "block";
  }
}

// Visualizador de Voucher / Comprobante
window.verVoucherReserva = function(codReserva) {
  const r = state.reservas.find(x => x.cod_reserva === codReserva);
  if (!r) return;

  const voucherContainer = document.getElementById("voucher-content");
  const fIngreso = formatDateTime(r.fecha_hora_ingreso);
  const fSalida = formatDateTime(r.fecha_hora_salida);
  const noches = calcularNoches(r.fecha_hora_ingreso, r.fecha_hora_salida);
  const precioNoche = parseFloat(r.precio_habitacion || 0);
  const totalTarifa = (noches * precioNoche).toFixed(2);

  voucherContainer.innerHTML = `
    <div class="voucher-card">
      <div class="voucher-header">
        <div>
          <div class="voucher-title">HOTEL CUMBRE REAL AIRPORT</div>
          <small class="text-muted">Arequipa, Perú &middot; Tel: +51 (54) 443210</small>
        </div>
        <div class="voucher-code">${r.cod_reserva}</div>
      </div>

      <div class="voucher-grid">
        <div>
          <div class="voucher-item-label">Huésped Titular:</div>
          <div class="voucher-item-val">${escapeHtml(r.huesped_nombre)}</div>
        </div>
        <div>
          <div class="voucher-item-label">Documento de Identidad:</div>
          <div class="voucher-item-val">${escapeHtml(r.doc_identidad)}</div>
        </div>
        <div>
          <div class="voucher-item-label">Habitación Asignada:</div>
          <div class="voucher-item-val">Habitación ${escapeHtml(r.num_habitacion || 'Pendiente')} (${escapeHtml(r.tipo_habitacion || 'Estándar')})</div>
        </div>
        <div>
          <div class="voucher-item-label">Tarifa por Noche:</div>
          <div class="voucher-item-val">S/ ${precioNoche.toFixed(2)}</div>
        </div>
        <div>
          <div class="voucher-item-label">Fecha Check-in:</div>
          <div class="voucher-item-val">${fIngreso}</div>
        </div>
        <div>
          <div class="voucher-item-label">Fecha Check-out:</div>
          <div class="voucher-item-val">${fSalida}</div>
        </div>
        <div>
          <div class="voucher-item-label">Estadía Programada:</div>
          <div class="voucher-item-val">${noches} noche(s)</div>
        </div>
        <div>
          <div class="voucher-item-label">Importe Estimado de Estadía:</div>
          <div class="voucher-item-val" style="color:var(--primary); font-size:16px;">S/ ${totalTarifa}</div>
        </div>
        <div>
          <div class="voucher-item-label">Servicio de Desayuno:</div>
          <div class="voucher-item-val">${r.solicita_desayuno ? '🍳 Incluido' : 'No contratado'}</div>
        </div>
        <div>
          <div class="voucher-item-label">Canal de Emisión:</div>
          <div class="voucher-item-val">${escapeHtml(r.medio_reserva_desc || r.cod_medioReserva)}</div>
        </div>
      </div>

      <div style="font-size: 12px; margin-top: 10px; padding: 10px; background:#f1f5f9; border-radius:6px;">
        <strong>Observaciones:</strong> ${escapeHtml(r.observaciones || 'Sin observaciones registradas.')}
      </div>

      <div class="voucher-footer-note">
        Emisor: Recepción AlojaGest &middot; Operador: ${escapeHtml(r.recepcionista_nombre || r.cod_recepcionista)} &middot; Fecha de Registro: ${r.fecha_reserva}
      </div>
    </div>
  `;

  document.getElementById("modal-voucher").classList.add("open");
};

/* ========================================================
   DIRECTORIO DE HUÉSPEDES
   ======================================================== */
async function loadHuespedes() {
  const tbody = document.getElementById("tbody-huespedes");
  try {
    const res = await fetch("/api/huespedes");
    const json = await res.json();

    if (json.success) {
      state.huespedes = json.data;
      renderHuespedes(state.huespedes);
    }
  } catch (err) {
    if (tbody) tbody.innerHTML = `<tr><td colspan="7" class="loading-td" style="color:var(--status-ocupada)">Error: ${err.message}</td></tr>`;
  }
}

function renderHuespedes(lista) {
  const tbody = document.getElementById("tbody-huespedes");
  const badge = document.getElementById("huespedes-count-badge");
  if (!tbody) return;

  badge.textContent = `${lista.length} de ${state.huespedes.length} clientes`;

  if (lista.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="loading-td">No se encontraron clientes con el criterio especificado.</td></tr>`;
    return;
  }

  tbody.innerHTML = lista.map(h => {
    const doc = escapeHtml(h.doc_identidad);
    const tipo = escapeHtml(h.tipo_doc_desc || h.cod_tipoDoc);
    const nombreCompleto = `${escapeHtml(h.nombres)} ${escapeHtml(h.apellidos)}`;
    const telefonos = escapeHtml(h.telefonos || "Sin registrar");
    const correo = escapeHtml(h.correo || "Sin correo");
    const reservas = h.total_reservas > 0 ? `<span class="badge badge-info">${h.total_reservas} reserva(s)</span>` : `<span class="badge badge-secondary">0</span>`;

    return `
      <tr>
        <td><b>${doc}</b></td>
        <td><span class="badge badge-secondary">${tipo}</span></td>
        <td>${nombreCompleto}</td>
        <td>📞 ${telefonos}</td>
        <td>✉️ ${correo}</td>
        <td>${reservas}</td>
        <td style="text-align: center;">
          <div class="table-actions">
            <button class="btn btn-secondary btn-sm" onclick="editarHuesped('${doc}')">✏️</button>
            <button class="btn btn-danger btn-sm" onclick="eliminarHuesped('${doc}', '${nombreCompleto}')">🗑️</button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

function filtrarHuespedes(termino) {
  if (!termino) {
    renderHuespedes(state.huespedes);
    return;
  }
  const filtrados = state.huespedes.filter(h => 
    h.doc_identidad.toLowerCase().includes(termino) ||
    h.nombres.toLowerCase().includes(termino) ||
    h.apellidos.toLowerCase().includes(termino) ||
    (h.correo && h.correo.toLowerCase().includes(termino))
  );
  renderHuespedes(filtrados);
}

function abrirModalHuesped(esEdicion, data = null) {
  state.modoEdicionHuesped = esEdicion;
  const modal = document.getElementById("modal-huesped");
  const modalTitle = document.getElementById("modal-huesped-title");
  const inputDoc = document.getElementById("input-huesped-doc");
  const inputTipoDoc = document.getElementById("input-huesped-tipodoc");
  const inputNombres = document.getElementById("input-huesped-nombres");
  const inputApellidos = document.getElementById("input-huesped-apellidos");
  const inputTelefono = document.getElementById("input-huesped-telefono");
  const inputCorreo = document.getElementById("input-huesped-correo");
  const alertBox = document.getElementById("huesped-alert");

  alertBox.style.display = "none";

  if (esEdicion && data) {
    modalTitle.textContent = "Modificar Ficha de Huésped";
    inputDoc.value = data.doc_identidad;
    inputDoc.disabled = true;
    inputTipoDoc.value = data.cod_tipoDoc;
    inputNombres.value = data.nombres;
    inputApellidos.value = data.apellidos;
    inputTelefono.value = data.telefonos || "";
    inputCorreo.value = data.correo || "";
  } else {
    modalTitle.textContent = "Registrar Nuevo Huésped";
    inputDoc.value = "";
    inputDoc.disabled = false;
    inputNombres.value = "";
    inputApellidos.value = "";
    inputTelefono.value = "";
    inputCorreo.value = "";
  }

  modal.classList.add("open");
}
window.abrirModalHuesped = abrirModalHuesped;

window.editarHuesped = function(docIdentidad) {
  const h = state.huespedes.find(x => x.doc_identidad === docIdentidad);
  if (h) abrirModalHuesped(true, h);
};

window.eliminarHuesped = async function(docIdentidad, nombre) {
  if (!confirm(`¿Eliminar al huésped "${nombre}" (Doc: ${docIdentidad})?\nSe darán de baja sus datos y reservas asociadas.`)) return;

  try {
    const res = await fetch(`/api/huespedes?doc_identidad=${encodeURIComponent(docIdentidad)}`, {
      method: "DELETE"
    });
    const json = await res.json();
    if (json.success) {
      showToast(json.message, "success");
      loadHuespedes();
      loadReservas();
      recargarDashboard();
      loadAuditoria();
    } else {
      showToast(`Error al eliminar: ${json.error}`, "error");
    }
  } catch (err) {
    showToast(`Error de red: ${err.message}`, "error");
  }
};

async function guardarHuesped() {
  const alertBox = document.getElementById("huesped-alert");
  const payload = {
    doc_identidad: document.getElementById("input-huesped-doc").value.trim(),
    cod_tipoDoc: document.getElementById("input-huesped-tipodoc").value,
    nombres: document.getElementById("input-huesped-nombres").value.trim(),
    apellidos: document.getElementById("input-huesped-apellidos").value.trim(),
    telefono: document.getElementById("input-huesped-telefono").value.trim(),
    correo: document.getElementById("input-huesped-correo").value.trim()
  };

  const method = state.modoEdicionHuesped ? "PUT" : "POST";
  try {
    const res = await fetch("/api/huespedes", {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const json = await res.json();

    if (json.success) {
      document.getElementById("modal-huesped").classList.remove("open");
      showToast(json.message, "success");
      loadHuespedes();
      recargarDashboard();
      loadAuditoria();
    } else {
      alertBox.textContent = json.error;
      alertBox.style.display = "block";
    }
  } catch (err) {
    alertBox.textContent = `Error de red: ${err.message}`;
    alertBox.style.display = "block";
  }
}

/* ========================================================
   CENTRO DE REPORTES Y ANALÍTICA (10 REPORTES OFICIALES)
   ======================================================== */
window.cargarReporteSeleccionado = function() {
  const select = document.getElementById("select-reporte-id");
  cargarReporte(select.value);
};

async function cargarReporte(reportId) {
  const titleDisplay = document.getElementById("report-title-display");
  const descDisplay = document.getElementById("report-desc-display");
  const countBadge = document.getElementById("report-count-badge");
  const thead = document.getElementById("thead-reporte");
  const tbody = document.getElementById("tbody-reporte");

  thead.innerHTML = "";
  tbody.innerHTML = `<tr><td colspan="6" class="loading-td">Ejecutando consulta en PostgreSQL...</td></tr>`;

  try {
    const res = await fetch(`/api/reportes/${reportId}`);
    const json = await res.json();

    if (json.success) {
      const rep = json.data;
      titleDisplay.textContent = rep.titulo;
      descDisplay.textContent = rep.descripcion;
      countBadge.textContent = `${rep.total_registros} registros encontrados`;

      if (rep.filas.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="loading-td">No se obtuvieron registros para esta consulta.</td></tr>`;
        return;
      }

      // Columnas automáticas
      const columnas = Object.keys(rep.filas[0]);
      thead.innerHTML = `<tr>${columnas.map(col => `<th>${formatearNombreColumna(col)}</th>`).join("")}</tr>`;

      tbody.innerHTML = rep.filas.map(fila => {
        return `
          <tr>
            ${columnas.map(col => {
              let val = fila[col];
              if (typeof val === "boolean") val = val ? "Sí" : "No";
              if (val === null || val === undefined) val = "-";
              return `<td>${escapeHtml(String(val))}</td>`;
            }).join("")}
          </tr>
        `;
      }).join("");
    } else {
      tbody.innerHTML = `<tr><td colspan="6" class="loading-td" style="color:var(--status-ocupada)">Error: ${json.error}</td></tr>`;
    }
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" class="loading-td" style="color:var(--status-ocupada)">Error de conexión: ${err.message}</td></tr>`;
  }
}

function formatearNombreColumna(col) {
  return col
    .replace(/_/g, " ")
    .replace(/\b\w/g, l => l.toUpperCase());
}

window.imprimirReporteActual = function() {
  window.print();
};

/* ========================================================
   AUDITORÍA Y SEGURIDAD
   ======================================================== */
async function loadAuditoria() {
  const tbody = document.getElementById("tbody-auditoria");
  try {
    const res = await fetch("/api/auditoria");
    const json = await res.json();

    if (json.success && json.data.length > 0) {
      tbody.innerHTML = json.data.map(log => {
        let opBadge = "badge-info";
        if (log.operacion === "INSERT") opBadge = "badge-success";
        if (log.operacion === "DELETE") opBadge = "badge-danger";
        if (log.operacion === "UPDATE") opBadge = "badge-warning";
        if (log.operacion === "CHECKIN") opBadge = "badge-success";
        if (log.operacion === "CHECKOUT") opBadge = "badge-warning";

        return `
          <tr>
            <td>#${log.id_auditoria}</td>
            <td><b>${escapeHtml(log.tabla_afectada)}</b></td>
            <td><span class="badge ${opBadge}">${escapeHtml(log.operacion)}</span></td>
            <td><code>${escapeHtml(log.registro_id)}</code></td>
            <td>${escapeHtml(log.detalle)}</td>
            <td>${formatDateTime(log.fecha_hora)}</td>
            <td><small>${escapeHtml(log.usuario_db)}</small></td>
          </tr>
        `;
      }).join("");
    } else {
      tbody.innerHTML = `<tr><td colspan="7" class="loading-td">No hay eventos registrados en la bitácora aún.</td></tr>`;
    }
  } catch (e) {
    console.error("Error al cargar auditoría:", e);
  }
}

/* ========================================================
   GESTIÓN DE PERSONAL (EXCLUSIVO ADMINISTRADOR)
   ======================================================== */
async function loadEmpleados() {
  const tbody = document.getElementById("tbody-empleados");
  if (!tbody) return;

  try {
    const res = await fetch("/api/empleados");
    const json = await res.json();

    if (json.success) {
      state.empleados = json.data;
      renderEmpleados(state.empleados);
    } else {
      tbody.innerHTML = `<tr><td colspan="8" class="loading-td" style="color:var(--status-ocupada)">Error: ${json.error}</td></tr>`;
    }
  } catch (err) {
    if (tbody) tbody.innerHTML = `<tr><td colspan="8" class="loading-td" style="color:var(--status-ocupada)">Error: ${err.message}</td></tr>`;
  }
}
window.loadEmpleados = loadEmpleados;

function renderEmpleados(lista) {
  const tbody = document.getElementById("tbody-empleados");
  if (!tbody) return;

  if (lista.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" class="loading-td">No se encontraron empleados registrados.</td></tr>`;
    return;
  }

  tbody.innerHTML = lista.map(emp => {
    const cod = escapeHtml(emp.cod_recepcionista);
    const nombres = escapeHtml(`${emp.nombres} ${emp.apellidos}`);
    const dni = escapeHtml(emp.dni || "-");
    const usuario = escapeHtml(emp.usuario || "-");
    const rol = emp.rol || "Recepcionista";
    const rolBadge = rol === "Administrador" ? "badge-role-admin" : "badge-role-recepcion";
    const estado = emp.estado || "Activo";
    const estadoBadge = estado === "Activo" ? "badge-success" : "badge-secondary";
    const reservasCount = emp.reservas_gestionadas || 0;

    const isCurrentAdmin = (state.session && state.session.cod_recepcionista === cod);

    return `
      <tr>
        <td><b>${cod}</b></td>
        <td><b>${nombres}</b></td>
        <td><code>${dni}</code></td>
        <td><code>${usuario}</code></td>
        <td><span class="badge ${rolBadge}">${rol}</span></td>
        <td><span class="badge ${estadoBadge}">${estado}</span></td>
        <td style="text-align: center;"><span class="badge badge-secondary">${reservasCount}</span></td>
        <td style="text-align: center;">
          <div class="table-actions">
            <button class="btn btn-secondary btn-sm" onclick="editarEmpleado('${cod}')" title="Modificar Datos">✏️ Editar</button>
            ${isCurrentAdmin ? '' : `
              <button class="btn btn-danger btn-sm" onclick="eliminarEmpleado('${cod}', '${escapeHtml(emp.nombres)}')" title="${estado === 'Activo' ? 'Desactivar' : 'Eliminar'}">
                ${estado === 'Activo' ? '🚫' : '🗑️'}
              </button>
            `}
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

function abrirModalEmpleado(esEdicion, data = null) {
  state.modoEdicionEmpleado = esEdicion;
  const modal = document.getElementById("modal-empleado");
  const modalTitle = document.getElementById("modal-empleado-title");
  const inputCod = document.getElementById("input-empleado-codigo");
  const inputNombres = document.getElementById("input-empleado-nombres");
  const inputApellidos = document.getElementById("input-empleado-apellidos");
  const inputDni = document.getElementById("input-empleado-dni");
  const inputUsuario = document.getElementById("input-empleado-usuario");
  const selectRol = document.getElementById("select-empleado-rol");
  const inputPass = document.getElementById("input-empleado-password");
  const alertBox = document.getElementById("empleado-alert");

  if (alertBox) alertBox.style.display = "none";

  if (esEdicion && data) {
    modalTitle.textContent = `Modificar Empleado ${data.cod_recepcionista}`;
    inputCod.value = data.cod_recepcionista;
    inputNombres.value = data.nombres || "";
    inputApellidos.value = data.apellidos || "";
    inputDni.value = data.dni || "";
    inputUsuario.value = data.usuario || "";
    selectRol.value = data.rol || "Recepcionista";
    inputPass.value = "";
    inputPass.placeholder = "Dejar en blanco para mantener la actual";
  } else {
    modalTitle.textContent = "Registrar Nuevo Empleado";
    inputCod.value = "";
    inputNombres.value = "";
    inputApellidos.value = "";
    inputDni.value = "";
    inputUsuario.value = "";
    selectRol.value = "Recepcionista";
    inputPass.value = "";
    inputPass.placeholder = "Dejar en blanco para usar DNI";
  }

  modal.classList.add("open");
}
window.abrirModalEmpleado = abrirModalEmpleado;

window.editarEmpleado = function(cod) {
  const emp = state.empleados.find(e => e.cod_recepcionista === cod);
  if (emp) {
    abrirModalEmpleado(true, emp);
  }
};

async function guardarEmpleado() {
  const alertBox = document.getElementById("empleado-alert");
  const cod = document.getElementById("input-empleado-codigo").value;
  const nombres = document.getElementById("input-empleado-nombres").value.trim();
  const apellidos = document.getElementById("input-empleado-apellidos").value.trim();
  const dni = document.getElementById("input-empleado-dni").value.trim();
  const usuario = document.getElementById("input-empleado-usuario").value.trim();
  const rol = document.getElementById("select-empleado-rol").value;
  const pass = document.getElementById("input-empleado-password").value.trim();

  if (!nombres || !apellidos || !dni || !usuario) {
    if (alertBox) {
      alertBox.textContent = "Por favor complete todos los campos obligatorios.";
      alertBox.style.display = "block";
    }
    return;
  }

  const payload = {
    nombres,
    apellidos,
    dni,
    usuario,
    rol,
    password: pass || dni
  };

  try {
    let res;
    if (state.modoEdicionEmpleado && cod) {
      payload.cod_recepcionista = cod;
      res = await fetch("/api/empleados", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    } else {
      res = await fetch("/api/empleados", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    }

    const json = await res.json();
    if (json.success) {
      showToast(json.message, "success");
      document.getElementById("modal-empleado").classList.remove("open");
      loadEmpleados();
      loadCatalogos();
      loadAuditoria();
    } else {
      if (alertBox) {
        alertBox.textContent = json.error || "Error al procesar empleado.";
        alertBox.style.display = "block";
      }
    }
  } catch (err) {
    if (alertBox) {
      alertBox.textContent = `Error de red: ${err.message}`;
      alertBox.style.display = "block";
    }
  }
}

window.eliminarEmpleado = async function(cod, nombre) {
  if (!confirm(`¿Está seguro de dar de baja al empleado ${nombre} (${cod})?\nSe validará la existencia de registros asociados en auditoría.`)) {
    return;
  }

  try {
    const res = await fetch(`/api/empleados?cod_recepcionista=${encodeURIComponent(cod)}`, {
      method: "DELETE"
    });
    const json = await res.json();
    if (json.success) {
      showToast(json.message, "success");
      loadEmpleados();
      loadCatalogos();
      loadAuditoria();
    } else {
      showToast(`Error: ${json.error}`, "error");
    }
  } catch (err) {
    showToast(`Error de conexión: ${err.message}`, "error");
  }
};

/* ========================================================
   UTILIDADES
   ======================================================== */
function getBadgeClass(estado) {
  switch (estado) {
    case "Disponible": return "badge-success";
    case "Reservada": return "badge-info";
    case "Ocupada": return "badge-danger";
    case "Limpieza": return "badge-warning";
    default: return "badge-secondary";
  }
}

function showToast(mensaje, tipo = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${tipo}`;
  toast.innerHTML = `<span>${tipo === 'success' ? '✅' : tipo === 'error' ? '❌' : 'ℹ️'}</span><span>${escapeHtml(mensaje)}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(15px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatDateTime(str) {
  if (!str) return "-";
  const d = new Date(str);
  if (isNaN(d.getTime())) return str;
  return `${d.toLocaleDateString("es-PE")} ${d.toLocaleTimeString("es-PE", { hour: '2-digit', minute: '2-digit' })}`;
}

function toInputDateTime(strOrDate) {
  if (!strOrDate) return "";
  const d = (strOrDate instanceof Date) ? strOrDate : new Date(strOrDate);
  if (isNaN(d.getTime())) return "";
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hours = String(d.getHours()).padStart(2, "0");
  const minutes = String(d.getMinutes()).padStart(2, "0");
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

function calcularNoches(inicio, fin) {
  const d1 = new Date(inicio);
  const d2 = new Date(fin);
  const diffTime = Math.abs(d2 - d1);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays > 0 ? diffDays : 1;
}
