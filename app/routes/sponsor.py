from fastapi import APIRouter, HTTPException
from app.models import Sponsor
from app.database import sponsors_collection
from app.auth import get_password_hash

router = APIRouter()

@router.post("/sponsor/register/", response_model=Sponsor)
async def register_sponsor(sponsor: Sponsor):
    """
    Registra un nuevo patrocinador en el sistema.

    Args:
        sponsor (Sponsor): Objeto que contiene los datos del patrocinador.

    Returns:
        Sponsor: El patrocinador creado con la contraseña hasheada.

    Raises:
        HTTPException: Si el email ya está en uso.
    """
    # Verificar si el email ya está en uso
    existing_sponsor = sponsors_collection.find_one({"email": sponsor.email})
    if existing_sponsor:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash de la contraseña
    hashed_password = get_password_hash(sponsor.password)
    
    # Crear el nuevo patrocinador
    sponsor_data = sponsor.dict()
    sponsor_data["password"] = hashed_password  # Almacenar la contraseña hasheada
    result = sponsors_collection.insert_one(sponsor_data)
    
    # Retornar el patrocinador creado
    created_sponsor = sponsors_collection.find_one({"_id": result.inserted_id})
    return Sponsor(**created_sponsor)
