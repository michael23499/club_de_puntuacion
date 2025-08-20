import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import administrators_collection

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Limpiar la colección antes de las pruebas
    administrators_collection.delete_many({})
    yield
    # Limpiar después de las pruebas (opcional, puedes comentar esta línea si no deseas limpiar)
    # administrators_collection.delete_many({})

def test_register_multiple_admins():
    # Registro del primer administrador
    response1 = client.post("/admin/register/", json={
        "name": "Admin User",  
        "email": "admin@example.com",
        "password": "root"
    })
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["email"] == "admin@example.com"
    assert data1["name"] == "Admin User"
    assert data1["role"] == "administrator"

    # Registro del segundo administrador
    response2 = client.post("/admin/register/", json={
        "name": "Admin User 2",  
        "email": "admin2@example.com",
        "password": "root2"
    })
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["email"] == "admin2@example.com"
    assert data2["name"] == "Admin User 2"
    assert data2["role"] == "administrator"

def test_register_admin_duplicate_email():
    response = client.post("/admin/register/", json={
        "name": "Admin User Duplicate",
        "email": "admin@example.com",  # Usar el mismo correo para probar duplicados
        "password": "root"
    })
    assert response.status_code == 400  # Cambia según cómo manejes errores de duplicados
    assert "detail" in response.json()  # Asegúrate de que se devuelve un mensaje de error
