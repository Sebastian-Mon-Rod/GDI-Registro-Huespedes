import urllib.request
import json
import sys

base_url = 'http://127.0.0.1:8000'

def test_endpoint(path, method='GET', data=None):
    url = base_url + path
    headers = {'Content-Type': 'application/json'} if data else {}
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode('utf-8') if data else None, 
        headers=headers, 
        method=method
    )
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = resp.read()
            return status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read()

print("--- TESTING ALOJAGEST LIVE SERVER ---")

# 1. Test Static Files
status, body = test_endpoint('/')
print(f"1. Static index.html: {status} (Bytes: {len(body)})")
assert status == 200, "Failed to load index.html"

status, body = test_endpoint('/styles.css')
print(f"2. Static styles.css: {status} (Bytes: {len(body)})")
assert status == 200, "Failed to load styles.css"

status, body = test_endpoint('/app.js')
print(f"3. Static app.js: {status} (Bytes: {len(body)})")
assert status == 200, "Failed to load app.js"

# 2. Test Auth Login (Admin & Receptionist)
status, body = test_endpoint('/api/auth/login', 'POST', {'usuario': 'admin', 'password': 'admin'})
data = json.loads(body.decode('utf-8'))
print(f"4. Auth Admin Login: {status} -> {data.get('message')} | User: {data.get('data', {}).get('usuario')} | Rol: {data.get('data', {}).get('rol')}")
assert status == 200 and data.get('data', {}).get('rol') == 'Administrador', "Admin login failed"

status, body = test_endpoint('/api/auth/login', 'POST', {'usuario': 'E002', 'password': '70000002'})
data = json.loads(body.decode('utf-8'))
print(f"5. Auth Receptionist Login: {status} -> {data.get('message')} | User: {data.get('data', {}).get('usuario')} | Rol: {data.get('data', {}).get('rol')}")
assert status == 200 and data.get('data', {}).get('rol') == 'Recepcionista', "Receptionist login failed"

# 3. Test Reservas API (no more 500 or JSON error)
status, body = test_endpoint('/api/reservas')
data = json.loads(body.decode('utf-8'))
reservas = data.get('data', [])
print(f"6. API Reservas: {status} -> Loaded {len(reservas)} reservations seamlessly!")
assert status == 200 and len(reservas) > 0, "Failed to load reservas"

# 4. Test Empleados API (Stored Procedures backed)
status, body = test_endpoint('/api/empleados')
data = json.loads(body.decode('utf-8'))
empleados = data.get('data', [])
print(f"7. API Empleados: {status} -> Loaded {len(empleados)} registered employees!")
assert status == 200 and len(empleados) > 0, "Failed to load empleados"

# 5. Test Reports BI 1 to 10
print("8. Testing 10 SQL Enterprise Reports:")
for i in range(1, 11):
    status, body = test_endpoint(f'/api/reportes/{i}')
    rep = json.loads(body.decode('utf-8'))
    rep_data = rep.get('data', {})
    print(f"   - Reporte #{i:02d}: [{rep_data.get('report_id')}] '{rep_data.get('titulo')}' -> {len(rep_data.get('filas', []))} filas")
    assert status == 200 and 'filas' in rep_data, f"Report {i} failed"

# 6. Test Dashboard & Habitaciones
status, body = test_endpoint('/api/dashboard')
dash = json.loads(body.decode('utf-8')).get('data', {})
print(f"9. Dashboard KPIs: Ocupación: {dash.get('tasa_ocupacion')}% | Libres: {dash.get('hab_disponibles')} | Ocupadas: {dash.get('hab_ocupadas')} | Reservadas: {dash.get('hab_reservadas')}")

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY 100%!")
