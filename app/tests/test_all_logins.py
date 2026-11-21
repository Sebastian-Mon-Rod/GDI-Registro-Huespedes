import urllib.request
import json

def test_login(u, p):
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/auth/login',
        data=json.dumps({'usuario': u, 'password': p}).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            user = data.get('data', {})
            print(f"Login '{u}': SUCCESS -> Status: {resp.status} | Name: {user.get('nombres')} | Rol: {user.get('rol')}")
            return True
    except urllib.error.HTTPError as e:
        print(f"Login '{u}': FAILED -> Status: {e.code} | {e.read().decode('utf-8')}")
        return False

print("--- TESTING ALL LOGIN CREDENTIALS ---")
assert test_login('JeanPiero', 'JeanPiero'), "JeanPiero login failed"
assert test_login('admin', 'admin'), "admin login failed"
assert test_login('E001', '10000001'), "E001 login failed"
assert test_login('E002', '70000002'), "E002 login failed"
assert test_login('luis.mendoza', '70000002'), "luis.mendoza login failed"
print("ALL LOGIN ACCOUNTS VERIFIED AND WORKING 100%!")
