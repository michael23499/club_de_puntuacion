import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import clients_collection

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Limpiar la colección antes de las pruebas
    clients_collection.delete_many({})
    yield
    # Limpiar después de las pruebas (opcional)
    # clients_collection.delete_many({})

def test_register_client():
    response = client.post("/clients/register/", json={
        "email": "test@example.com",
        "password": "password123",
        "name": "Test Client"
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["email"] == "test@example.com"

def test_login_client():
    response = client.post("/clients/login/", data={"username": "test@example.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_client():
    # Primero, registra un cliente
    response = client.post("/clients/register/", json={
        "email": "test2@example.com",
        "password": "password123",
        "name": "Test Client 2"
    })
    assert response.status_code == 200, f"Error al registrar el cliente: {response.content}"
    
    # Intenta obtener el ID
    try:
        client_id = response.json()["id"]
    except KeyError:
        raise KeyError(f"No se encontró 'id' en la respuesta: {response.json()}")

    # Iniciar sesión para obtener el token de autenticación
    login_response = client.post("/clients/login/", data={"username": "test2@example.com", "password": "password123"})
    assert login_response.status_code == 200, f"Error al iniciar sesión: {login_response.content}"
    
    token = login_response.json().get("access_token")  # Ajusta según cómo devuelvas el token

    # Ahora intenta obtener el cliente registrado con el token
    response = client.get(f"/clients/{client_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, f"Error al obtener el cliente: {response.content}"
    data = response.json()
    assert data["email"] == "test2@example.com"
