import pytest
from fastapi.testclient import TestClient
from app.main import app 
from app.database import establishments_collection

test_client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Limpiar la colección antes de las pruebas
    establishments_collection.delete_many({})
    yield
    # No limpiar la colección después de las pruebas para mantener los datos

def test_register_establishment_1():
    response = test_client.post("/establishments/register/", json={
        "name": "Mcdonalds",
        "location": "Madrid",
        "email": "mcdonalds@gmail.com",
        "password": "123"
    })
    
    assert response.status_code == 200  # Verifica que la inserción fue exitosa
    data = response.json()
    assert "id" in data  # Verifica que se ha creado un ID
    assert data["name"] == "Mcdonalds"  # Verifica el nombre

def test_register_establishment_2():
    response = test_client.post("/establishments/register/", json={
        "name": "Burger King",
        "location": "Barcelona",
        "email": "burgerking@gmail.com",
        "password": "456"
    })
    
    assert response.status_code == 200  # Verifica que la inserción fue exitosa
    data = response.json()
    assert "id" in data  # Verifica que se ha creado un ID
    assert data["name"] == "Burger King"  # Verifica el nombre
