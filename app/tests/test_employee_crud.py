import urllib.request
import json

base_url = 'http://127.0.0.1:8000'

def request(path, method='GET', data=None):
    url = base_url + path
    headers = {'Content-Type': 'application/json'} if data else {}
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode('utf-8') if data else None, 
        headers=headers, 
        method=method
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))

print("=== TESTING EMPLOYEE CRUD VIA STORED PROCEDURES ===")

# 1. Create a new employee
new_emp = {
    "nombres": "Fernando",
    "apellidos": "Salazar Prado",
    "dni": "78912345",
    "usuario": "fernando.salazar",
    "rol": "Recepcionista",
    "password": "mi_password_seguro_123"
}
status, res = request('/api/empleados', 'POST', new_emp)
print(f"1. Create Employee: {status} -> {res.get('message')}")
assert status == 200 and res.get('success'), "Failed to create employee"

# 2. Verify employee in list
status, res = request('/api/empleados')
emps = res.get('data', [])
created = next((e for e in emps if e.get('dni') == '78912345'), None)
assert created is not None, "Created employee not found in list"
cod_emp = created['cod_recepcionista']
print(f"2. Verified in List: {cod_emp} - {created['nombres']} {created['apellidos']} (Rol: {created['rol']}, DNI: {created['dni']})")

# 3. Test Login with newly created employee
status, res = request('/api/auth/login', 'POST', {'usuario': 'fernando.salazar', 'password': 'mi_password_seguro_123'})
print(f"3. Login with New Employee: {status} -> {res.get('message')}")
assert status == 200 and res.get('data', {}).get('cod_recepcionista') == cod_emp, "Login failed for new employee"

# 4. Modify employee (promote to Administrador)
update_emp = {
    "cod_recepcionista": cod_emp,
    "nombres": "Fernando",
    "apellidos": "Salazar Prado",
    "dni": "78912345",
    "usuario": "fernando.admin",
    "rol": "Administrador",
    "password": "nueva_password_admin"
}
status, res = request('/api/empleados', 'PUT', update_emp)
print(f"4. Modify Employee: {status} -> {res.get('message')}")
assert status == 200 and res.get('success'), "Failed to update employee"

# 5. Verify updated role in login
status, res = request('/api/auth/login', 'POST', {'usuario': 'fernando.admin', 'password': 'nueva_password_admin'})
print(f"5. Login with Updated Role: {status} -> Rol is now: {res.get('data', {}).get('rol')}")
assert res.get('data', {}).get('rol') == 'Administrador', "Role update failed"

# 6. Deactivate employee (sp_eliminar_recepcionista)
status, res = request(f'/api/empleados?cod_recepcionista={cod_emp}', 'DELETE')
print(f"6. Deactivate/Delete Employee: {status} -> {res.get('message')}")
assert status == 200 and res.get('success'), "Failed to deactivate employee"

# 7. Verify inactive employee can no longer login
try:
    status, res = request('/api/auth/login', 'POST', {'usuario': 'fernando.admin', 'password': 'nueva_password_admin'})
    raise AssertionError("Inactive employee should not be able to log in!")
except urllib.error.HTTPError as e:
    print(f"7. Inactive Employee Login Blocked as expected: HTTP {e.code}")

print("\nALL EMPLOYEE CRUD & SECURITY TESTS PASSED 100%!")
