from fastapi import APIRouter, HTTPException, Depends
from app.models import Administrator
from app.database import administrators_collection
from app.auth import get_password_hash

router = APIRouter()

# ID del primer administrador
ROOT_ADMIN_EMAIL = "root_admin@example.com"

@router.post("/admin/register/", response_model=Administrator)
async def register_administrator(admin: Administrator):
    """
    Registra un nuevo administrador.

    Args:
        admin (Administrator): Datos del nuevo administrador.

    Returns:
        Administrator: El administrador creado.

    Raises:
        HTTPException: Si el email ya está en uso.
    """
    # Verificar si el email ya está en uso
    existing_admin = administrators_collection.find_one({"email": admin.email})
    if existing_admin:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash de la contraseña
    hashed_password = get_password_hash(admin.password)
    
    # Crear el nuevo administrador
    admin_data = admin.dict()
    admin_data["password"] = hashed_password
    result = administrators_collection.insert_one(admin_data)
    
    # Retornar el administrador creado
    created_admin = administrators_collection.find_one({"_id": result.inserted_id})
    return Administrator(**created_admin)

@router.get("/admin/access-all/")
async def access_all_admin_features(email: str):
    """
    Acceso total a funciones administrativas sin necesidad de token.

    Args:
        email (str): Correo electrónico del administrador.

    Returns:
        str: Mensaje de acceso concedido.

    Raises:
        HTTPException: Si el administrador no tiene acceso.
    """
    # Verificar si el email corresponde al administrador root
    if email != ROOT_ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return "Access granted to all admin features."
