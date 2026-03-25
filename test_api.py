#!/usr/bin/env python3
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
TIMEOUT = 5

def print_test(name: str, method: str, endpoint: str):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"Method: {method} | Endpoint: {endpoint}")
    print(f"URL: {BASE_URL}{endpoint}")

def print_response(response: requests.Response):
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

# Test 1: Verify API is responding
print_test("Health Check", "GET", "/docs")
try:
    response = requests.get(f"{BASE_URL}/docs", timeout=TIMEOUT)
    print_response(response)
except Exception as e:
    print(f"ERROR: {e}")

# Test 2: Create a Role
print_test("Create Role", "POST", "/roles/")
try:
    payload = {"name": "test_role"}
    response = requests.post(
        f"{BASE_URL}/roles/",
        json=payload,
        timeout=TIMEOUT
    )
    print_response(response)
    role_data = response.json() if response.ok else None
except Exception as e:
    print(f"ERROR: {e}")

# Test 3: List Roles
print_test("List Roles", "GET", "/roles/")
try:
    response = requests.get(f"{BASE_URL}/roles/", timeout=TIMEOUT)
    print_response(response)
except Exception as e:
    print(f"ERROR: {e}")

# Test 4: Create Direction Régionale
print_test("Create Direction Régionale", "POST", "/directions-regionales/")
try:
    payload = {
        "nom": "Direction Nord",
        "gouvernorat": "Tunis"
    }
    response = requests.post(
        f"{BASE_URL}/directions-regionales/",
        json=payload,
        timeout=TIMEOUT
    )
    print_response(response)
    region_data = response.json() if response.ok else None
    region_id = region_data.get("id") if region_data else None
except Exception as e:
    print(f"ERROR: {e}")
    region_id = None

# Test 5: List Directions Régionales
print_test("List Directions Régionales", "GET", "/directions-regionales/")
try:
    response = requests.get(f"{BASE_URL}/directions-regionales/", timeout=TIMEOUT)
    print_response(response)
except Exception as e:
    print(f"ERROR: {e}")

# Test 6: Get Direction Régionale by ID
if region_id:
    print_test("Get Direction Régionale", "GET", f"/directions-regionales/{region_id}")
    try:
        response = requests.get(
            f"{BASE_URL}/directions-regionales/{region_id}",
            timeout=TIMEOUT
        )
        print_response(response)
    except Exception as e:
        print(f"ERROR: {e}")

# Test 7: Create Direction Secondaire
if region_id:
    print_test("Create Direction Secondaire", "POST", "/directions-secondaires/")
    try:
        payload = {
            "nom": "Antenne Centre",
            "region_id": region_id
        }
        response = requests.post(
            f"{BASE_URL}/directions-secondaires/",
            json=payload,
            timeout=TIMEOUT
        )
        print_response(response)
        secondaire_data = response.json() if response.ok else None
        secondaire_id = secondaire_data.get("id") if secondaire_data else None
    except Exception as e:
        print(f"ERROR: {e}")
        secondaire_id = None

# Test 8: List Directions Secondaires
print_test("List Directions Secondaires", "GET", "/directions-secondaires/")
try:
    response = requests.get(f"{BASE_URL}/directions-secondaires/", timeout=TIMEOUT)
    print_response(response)
except Exception as e:
    print(f"ERROR: {e}")

# Test 9: Create User
print_test("Create User", "POST", "/users/")
try:
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "role_id": 1
    }
    response = requests.post(
        f"{BASE_URL}/users/",
        json=payload,
        timeout=TIMEOUT
    )
    print_response(response)
    user_data = response.json() if response.ok else None
    user_id = user_data.get("id") if user_data else None
except Exception as e:
    print(f"ERROR: {e}")
    user_id = None

# Test 10: List Users
print_test("List Users", "GET", "/users/")
try:
    response = requests.get(f"{BASE_URL}/users/", timeout=TIMEOUT)
    print_response(response)
except Exception as e:
    print(f"ERROR: {e}")

# Test 11: Create Forest
print_test("Create Forest", "POST", "/forests/")
try:
    payload = {
        "name": "Forêt Test",
        "description": "Forest de test",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [10.0, 36.0],
                [10.5, 36.0],
                [10.5, 36.5],
                [10.0, 36.5],
                [10.0, 36.0]
            ]]
        },
        "created_by_id": user_id
    }
    response = requests.post(
        f"{BASE_URL}/forests/",
        json=payload,
        timeout=TIMEOUT
    )
    print_response(response)
    forest_data = response.json() if response.ok else None
    forest_id = forest_data.get("id") if forest_data else None
except Exception as e:
    print(f"ERROR: {e}")
    forest_id = None

# Test 12: List Forests
print_test("List Forests", "GET", "/forests/")
try:
    response = requests.get(f"{BASE_URL}/forests/", timeout=TIMEOUT)
    print_response(response)
except Exception as e:
    print(f"ERROR: {e}")

# Test 13: Create Parcelle
if forest_id:
    print_test("Create Parcelle", "POST", "/parcelles/")
    try:
        payload = {
            "forest_id": forest_id,
            "name": "Parcelle 1",
            "description": "First plot",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [10.0, 36.0],
                    [10.2, 36.0],
                    [10.2, 36.2],
                    [10.0, 36.2],
                    [10.0, 36.0]
                ]]
            },
            "created_by_id": user_id
        }
        response = requests.post(
            f"{BASE_URL}/parcelles/",
            json=payload,
            timeout=TIMEOUT
        )
        print_response(response)
        parcelle_data = response.json() if response.ok else None
        parcelle_id = parcelle_data.get("id") if parcelle_data else None
    except Exception as e:
        print(f"ERROR: {e}")
        parcelle_id = None

# Test 14: List Parcelles
print_test("List Parcelles", "GET", "/parcelles/")
try:
    response = requests.get(f"{BASE_URL}/parcelles/", timeout=TIMEOUT)
    print_response(response)
except Exception as e:
    print(f"ERROR: {e}")

print(f"\n{'='*60}")
print("TESTS COMPLETED")
print(f"{'='*60}\n")
