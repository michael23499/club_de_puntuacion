from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime
from typing import List, Optional # Asegúrate de importar List
from app.models import Establishment, EstablishmentCreate, PointsAssignment, PointsPolicy, Transaction
from app.database import db, clients_collection  
from app.auth import get_current_user, create_access_token, get_password_hash, role_required, verify_password
from fastapi.security import OAuth2PasswordRequestForm
from bson import ObjectId
import re

router = APIRouter()

def validate_email(email: str):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise HTTPException(status_code=400, detail="Invalid email format.")

def validate_points_policy(policy: PointsPolicy):
    required_fields = ["min_points", "max_points", "expiration_days"]
    for field in required_fields:
        if field not in policy.dict():
            raise HTTPException(status_code=400, detail=f"{field} is required in points policy.")
    if policy.min_points < 0 or policy.max_points < 0:
        raise HTTPException(status_code=400, detail="Points must be non-negative.")

@router.post("/establishments/register/", response_model=Establishment)
async def register_establishment(establishment: EstablishmentCreate):
    validate_email(establishment.email)

    existing_establishment = db.establishments.find_one({"email": establishment.email})
    if existing_establishment:
        raise HTTPException(status_code=400, detail="Establishment already exists.")

    establishment_data = establishment.dict(exclude_unset=True)
    establishment_data["role"] = "establishment"
    establishment_data["points_distribution_history"] = []
    establishment_data["points_policy"] = {}  # Inicializar política de puntos
    establishment_data["password"] = get_password_hash(establishment.password)

    try:
        result = db.establishments.insert_one(establishment_data)
        establishment_data["id"] = str(result.inserted_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error creating establishment: " + str(e))

    return establishment_data

@router.post("/establishments/login/")
async def login_establishment(form_data: OAuth2PasswordRequestForm = Depends()):
    establishment = db.establishments.find_one({"email": form_data.username})
    if not establishment:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if not verify_password(form_data.password, establishment.get('password', '')):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": establishment['email'], "role": establishment['role']})
    return {"access_token": access_token, "token_type": "bearer"}

@router.put("/establishments/{establishment_id}/points-policy/", response_model=dict)
async def update_points_policy(establishment_id: str, policy: PointsPolicy, current_user: Establishment = Depends(get_current_user)):
    if current_user.role != "establishment":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource.")

    if not ObjectId.is_valid(establishment_id):
        raise HTTPException(status_code=400, detail="Invalid establishment ID format.")

    validate_points_policy(policy)

    establishment = db.establishments.find_one({"_id": ObjectId(establishment_id)})
    if establishment is None:
        raise HTTPException(status_code=404, detail="Establishment not found")

    try:
        db.establishments.update_one(
            {"_id": ObjectId(establishment_id)},
            {"$set": {"points_policy": policy.dict()}}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error updating points policy: " + str(e))

    return {"detail": "Points policy updated successfully"}

@router.post("/establishments/{establishment_id}/assign-points/", response_model=dict)
async def assign_points(establishment_id: str, assignment: PointsAssignment):
    # Validar el formato del ID del establecimiento
    if not ObjectId.is_valid(establishment_id):
        raise HTTPException(status_code=400, detail="Invalid establishment ID format.")

    # Buscar el establecimiento en la base de datos
    establishment = db.establishments.find_one({"_id": ObjectId(establishment_id)})
    if establishment is None:
        raise HTTPException(status_code=404, detail="Establishment not found")

    # Obtener la fecha actual y formatearla
    formatted_date = datetime.utcnow().strftime("%d-%m-%y %H:%M")  # Formato DD-MM-YY HH:MM

    # Crear un nuevo registro de distribución de puntos
    new_distribution_record = {
        "points": assignment.points,
        "date": formatted_date,  # Usar la fecha formateada
        "reason": assignment.reason
    }
    # Actualizar el establecimiento para agregar el nuevo registro a points_distribution_history
    try:
        db.establishments.update_one(
            {"_id": ObjectId(establishment_id)},
            {"$push": {"points_distribution_history": new_distribution_record}}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error assigning points: " + str(e))

    return {
        "detail": "Points assigned successfully",
        "distribution_record": new_distribution_record
    }

@router.get("/establishments/reportes/uso", response_model=List[dict])
async def obtener_reporte_uso(
    client_id: str,
    fecha: Optional[str] = Query(None, description="Fecha en formato 'dd-mm-yy'"),
    hora: Optional[str] = Query(None, description="Hora en formato 'HH:MM'"),
    current_user: Establishment = Depends(role_required("establishment"))  # Verifica que el usuario sea un establecimiento
):
    # Validar el ID del cliente
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=400, detail="ID de cliente inválido")

    # Validar el formato de la fecha
    if fecha and not re.match(r'^\d{2}-\d{2}-\d{2}$', fecha):
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Debe ser 'dd-mm-yy'.")

    # Validar el formato de la hora
    if hora and not re.match(r'^\d{2}:\d{2}$', hora):
        raise HTTPException(status_code=400, detail="Formato de hora inválido. Debe ser 'HH:MM'.")

    try:
        # Buscar al cliente en la base de datos
        cliente = clients_collection.find_one({"_id": ObjectId(client_id)})
        if cliente is None:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # Obtener el historial de consumo de puntos
        historia_consumo = cliente.get("points_consumption_history", [])

        # Filtrar por fecha y hora
        reportes_filtrados = []
        for registro in historia_consumo:
            fecha_registro = registro.get("date", "")
            hora_registro = fecha_registro.split(" ")[1] if " " in fecha_registro else ""

            # Verificar coincidencias
            if (fecha is None or fecha in fecha_registro) and (hora is None or hora in hora_registro):
                reportes_filtrados.append(registro)

        return reportes_filtrados

    except Exception as e:
        # Manejo de excepciones inesperadas
        raise HTTPException(status_code=500, detail="Error interno del servidor. Por favor, inténtelo de nuevo más tarde.")
