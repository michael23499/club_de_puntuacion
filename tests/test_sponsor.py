import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import sponsors_collection

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Limpiar la colección antes de las pruebas
    sponsors_collection.delete_many({})
    yield
    # Limpiar después de las pruebas (opcional, puedes comentar esta línea si no deseas limpiar)
    # sponsors_collection.delete_many({})

def test_register_multiple_sponsors():
    # Registro del primer patrocinador
    response1 = client.post("/sponsor/register/", json={
        "name": "Michael",  
        "email": "michael@example.com",
        "password": "sponsorpass1"
    })
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["email"] == "michael@example.com"
    assert data1["name"] == "Michael"  # Verificar el nombre
    assert "role" in data1  # Verificar que se devuelve el rol
    assert data1["role"] == "sponsor"  # Asegúrate de que el rol sea correcto

    # Registro del segundo patrocinador
    response2 = client.post("/sponsor/register/", json={
        "name": "Sarah",  
        "email": "sarah@example.com",
        "password": "sponsorpass2"
    })
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["email"] == "sarah@example.com"
    assert data2["name"] == "Sarah"  # Verificar el nombre
    assert "role" in data2  # Verificar que se devuelve el rol
    assert data2["role"] == "sponsor"  # Asegúrate de que el rol sea correcto

def test_register_sponsor_duplicate_email():
    response = client.post("/sponsor/register/", json={
        "name": "Duplicate Michael",  # Cambiar el nombre para evitar confusiones
        "email": "michael@example.com",  # Usar el mismo correo para probar duplicados
        "password": "sponsorpass"
    })
    assert response.status_code == 400  # Cambia según cómo manejes errores de duplicados
    assert "detail" in response.json()  # Asegúrate de que se devuelve un mensaje de error
