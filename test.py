import requests

N8N_URL = "http://localhost:5678"
EMAIL = "mlpvirtualsolutions@gmail.com"
PASSWORD = "GrandmaLucy9225!"
# PASSWORD = "8eLegendary"



def test_n8n_connection():
    print(f"Testing connection to n8n at {N8N_URL}...")

    # Check if n8n is reachable at all
    try:
        r = requests.get(N8N_URL, timeout=5)
        print(f"  Reachable: YES (status {r.status_code})")
    except requests.exceptions.ConnectionError:
        print("  Reachable: NO — n8n is not running or wrong URL/port")
        return
    except requests.exceptions.Timeout:
        print("  Reachable: NO — connection timed out")
        return

    # Attempt login via n8n REST API
    login_url = f"{N8N_URL}/rest/login"
    payload = {"emailOrLdapLoginId": EMAIL, "password": PASSWORD}

    try:
        r = requests.post(login_url, json=payload, timeout=5)
        if r.status_code == 200:
            print(f"  Login: SUCCESS")
            data = r.json()
            print(f"  User: {data.get('data', {}).get('email', 'unknown')}")
        elif r.status_code == 401:
            print(f"  Login: FAILED — wrong email or password (401)")
        elif r.status_code == 404:
            print(f"  Login endpoint not found (404) — trying /rest/users/login...")
            r2 = requests.post(f"{N8N_URL}/rest/users/login", json=payload, timeout=5)
            if r2.status_code == 200:
                print(f"  Login: SUCCESS (legacy endpoint)")
            else:
                print(f"  Login: FAILED (status {r2.status_code}): {r2.text[:200]}")
        else:
            print(f"  Login: FAILED (status {r.status_code}): {r.text[:200]}")
    except requests.exceptions.RequestException as e:
        print(f"  Login: ERROR — {e}")


if __name__ == "__main__":
    test_n8n_connection()
