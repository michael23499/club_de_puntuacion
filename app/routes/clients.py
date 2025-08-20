from fastapi import APIRouter, HTTPException, Depends
from app.database import clients_collection
from app.models import Client, PointsResponse, RedeemPointsRequest, Transaction
from app.auth import get_current_user, create_access_token, get_password_hash, verify_password
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from bson import ObjectId
import re
import logging

# Crear un router de FastAPI para manejar las rutas relacionadas con los clientes
router = APIRouter()

# Configuración del registro de errores
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constantes para el manejo de puntos
POINTS_LIMIT_PER_TRANSACTION = 3000  # Límite de puntos por transacción
POINTS_EXPIRATION_DAYS = 90  # Días hasta que los puntos expiran

def validate_email(email: str):
    """
    Valida el formato del correo electrónico utilizando una expresión regular.

    Args:
        email (str): El correo electrónico a validar.

    Raises:
        HTTPException: Si el formato del correo electrónico no es válido.
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise HTTPException(status_code=400, detail="Formato de correo electrónico no válido.")

@router.post("/clients/register/", response_model=Client)
def register_client(client: Client):
    """
    Registra un nuevo cliente en la base de datos.

    Args:
        client (Client): El objeto cliente que contiene la información del nuevo cliente.

    Returns:
        Client: El cliente registrado con su ID asignado.

    Raises:
        HTTPException: Si hay un error al registrar el cliente.
    """
    try:
        validate_email(client.email)  # Validar el correo electrónico

        # Verificar si el correo ya existe en la base de datos
        existing_client = clients_collection.find_one({"email": client.email})
        if existing_client:
            raise HTTPException(status_code=400, detail=f"El correo electrónico '{client.email}' ya está registrado.")

        client.password = get_password_hash(client.password)  # Asegúrate de que la contraseña esté hashada
        client.role = "client"  # Asignar rol por defecto
        client_dict = client.dict(exclude_unset=True)
        client_dict["transaction_history"] = []  # Inicializar el historial de transacciones
        client_dict["points_consumption_history"] = []  # Inicializar el historial de consumo de puntos

        # Insertar en la colección y obtener el ID
        result = clients_collection.insert_one(client_dict)

        # Asignar el ID generado por MongoDB al modelo
        client.id = str(result.inserted_id)  # Convertir a string si es necesario

        # Retornar el cliente con el ID
        return client
    except HTTPException as http_ex:
        raise http_ex  # Re-lanzar excepciones HTTP
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al registrar el cliente.")

@router.post("/clients/login/")
def login_client(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Inicia sesión de un cliente y genera un token de acceso.

    Args:
        form_data (OAuth2PasswordRequestForm): Datos del formulario de inicio de sesión.

    Returns:
        dict: Un diccionario que contiene el token de acceso y su tipo.

    Raises:
        HTTPException: Si el usuario o la contraseña son incorrectos.
    """
    user = clients_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user['password']):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos.")
    access_token = create_access_token(data={"sub": user['email']})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/clients/{client_id}/", response_model=Client)
def get_client(client_id: str, current_user: Client = Depends(get_current_user)):
    """
    Obtiene la información de un cliente específico.

    Args:
        client_id (str): El ID del cliente a obtener.
        current_user (Client): El usuario actualmente autenticado.

    Returns:
        Client: El objeto cliente correspondiente.

    Raises:
        HTTPException: Si el ID del cliente no es válido o no se encuentra el cliente.
    """
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=400, detail="Formato de ID de cliente no válido.")
    
    client = clients_collection.find_one({"_id": ObjectId(client_id)})
    if client is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")
    
    client['id'] = str(client['_id'])  # Convertir el ObjectId a string para el modelo
    return Client(**client)  

@router.get("/clients/{client_id}/points/", response_model=PointsResponse)
def get_client_points(client_id: str, current_user: Client = Depends(get_current_user)):
    """
    Obtiene la cantidad de puntos de un cliente específico.

    Args:
        client_id (str): El ID del cliente.
        current_user (Client): El usuario actualmente autenticado.

    Returns:
        PointsResponse: Un objeto que contiene la cantidad de puntos del cliente.

    Raises:
        HTTPException: Si el ID del cliente no es válido o no se encuentra el cliente.
    """
    try:
        if not ObjectId.is_valid(client_id):
            raise HTTPException(status_code=400, detail="Formato de ID de cliente no válido.")
        
        # Verificar si el client_id corresponde al usuario autenticado
        if current_user.id != client_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para acceder a estos puntos.")
        
        client = clients_collection.find_one({"_id": ObjectId(client_id)})
        if client is None:
            raise HTTPException(status_code=404, detail="Cliente no encontrado.")
        
        points = client.get('points', 0)
        return PointsResponse(points=points, message=f"Este cliente posee {points} puntos.")
    except HTTPException as http_ex:
        raise http_ex  # Re-lanzar excepciones HTTP
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener los puntos del cliente.")

@router.post("/clients/{client_id}/transactions/", response_model=Transaction)
def register_transaction(client_id: str, transaction: Transaction, current_user: Client = Depends(get_current_user)):
    """
    Registra una nueva transacción para un cliente.

    Args:
        client_id (str): El ID del cliente.
        transaction (Transaction): Los detalles de la transacción a registrar.
        current_user (Client): El usuario actualmente autenticado.

    Returns:
        Transaction: El registro de la transacción.

    Raises:
        HTTPException: Si hay un error al registrar la transacción.
    """
    try:
        # Validar el formato del ID del cliente
        if not ObjectId.is_valid(client_id):
            raise HTTPException(status_code=400, detail="Formato de ID de cliente no válido.")
        
        # Verificar si el cliente existe
        client = clients_collection.find_one({"_id": ObjectId(client_id)})
        if client is None:
            raise HTTPException(status_code=404, detail="Cliente no encontrado.")
        
        # Validar la transacción
        if transaction.amount_spent <= 0:
            raise HTTPException(status_code=400, detail="El monto gastado debe ser positivo.")
        if not transaction.establishment_id or not transaction.description:
            raise HTTPException(status_code=400, detail="El establecimiento y la descripción son obligatorios.")

        # Calcular puntos
        points_earned = min(int(transaction.amount_spent * 10), POINTS_LIMIT_PER_TRANSACTION)

        # Asegurarse de que transaction_history sea una lista antes de hacer el push
        if not isinstance(client.get('transaction_history'), list):
            clients_collection.update_one(
                {"_id": ObjectId(client_id)},
                {"$set": {"transaction_history": []}}
            )

        # Asignar la fecha y hora actuales automáticamente y formatearlas
        transaction_date = datetime.now()
        formatted_date = transaction_date.strftime("%d-%m-%y %H:%M")  # Formato DD MM YY HH:MM

        # Crear el registro de la transacción
        transaction_record = {
            "establishment_id": transaction.establishment_id,
            "points": points_earned,
            "description": transaction.description,
            "amount_spent": transaction.amount_spent,
            "date": formatted_date  # Usar la fecha formateada
        }

        # Agregar la nueva transacción
        clients_collection.update_one(
            {"_id": ObjectId(client_id)},
            {
                "$push": {"transaction_history": transaction_record},
                "$inc": {"points": points_earned}
            }
        )

        return transaction_record
    except HTTPException as http_ex:
        raise http_ex  # Re-lanzar excepciones HTTP
    except Exception as e:
        logger.error("Error inesperado: %s", e)
        raise HTTPException(status_code=500, detail="Error al registrar la transacción.")

@router.post("/clients/{client_id}/redeem/")
def redeem_points(client_id: str, request: RedeemPointsRequest, current_user: Client = Depends(get_current_user)):
    """
    Redime puntos de un cliente.

    Args:
        client_id (str): El ID del cliente.
        request (RedeemPointsRequest): Detalles de la solicitud de redención de puntos.
        current_user (Client): El usuario actualmente autenticado.

    Returns:
        dict: Un mensaje de éxito de la redención.

    Raises:
        HTTPException: Si hay un error al redimir puntos.
    """
    try:
        # Validar el formato del ID del cliente
        if not ObjectId.is_valid(client_id):
            raise HTTPException(status_code=400, detail="Formato de ID de cliente no válido.")
        
        # Verificar si el cliente existe
        client = clients_collection.find_one({"_id": ObjectId(client_id)})
        if client is None:
            raise HTTPException(status_code=404, detail="Cliente no encontrado.")

        # Validar la cantidad de puntos a redimir
        if request.points <= 0:
            raise HTTPException(status_code=400, detail="La cantidad de puntos a redimir debe ser positiva.")
        
        if client['points'] < request.points:
            raise HTTPException(status_code=400, detail="Puntos insuficientes.")
        
        # Registrar el consumo de puntos
        consumption_record = {
            "points_consumed": -request.points,  # Cambia 'points' a 'points_consumed'
            "description": request.description,
            "date": datetime.now().strftime("%d-%m-%y %H:%M"),  # Formato de fecha y hora
            "expiration_date": (datetime.now() + timedelta(days=POINTS_EXPIRATION_DAYS)).strftime("%d-%m-%y %H:%M")  # Fecha de caducidad
        }

        # Actualizar los puntos del cliente y agregar el registro de consumo en una sola operación
        result = clients_collection.update_one(
            {"_id": ObjectId(client_id)},
            {
                "$inc": {"points": -request.points},  # Restar puntos
                "$push": {"points_consumption_history": consumption_record}  # Agregar el registro de consumo
            }
        )

        # Verificar si la actualización fue exitosa
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Error al redimir puntos.")

        return {
            "message": f"Puntos redimidos con éxito. Gastaste {request.points} puntos."
        }
    except HTTPException as http_ex:
        raise http_ex  # Re-lanzar excepciones HTTP
    except Exception as e:
        logger.error("Error inesperado: %s", e)
        raise HTTPException(status_code=500, detail="Error al redimir puntos.")

@router.get("/clients/{client_id}/points_consumption_history/")
def get_points_consumption_history(client_id: str, current_user: Client = Depends(get_current_user)):
    """
    Obtiene el historial de consumo de puntos de un cliente.

    Args:
        client_id (str): El ID del cliente.
        current_user (Client): El usuario actualmente autenticado.

    Returns:
        list: Una lista del historial de consumo de puntos.

    Raises:
        HTTPException: Si el ID del cliente no es válido o no se encuentra el cliente.
    """
    try:
        # Validar el formato del ID del cliente
        if not ObjectId.is_valid(client_id):
            logger.warning("Intento de acceso con un ID de cliente no válido: %s", client_id)
            raise HTTPException(status_code=400, detail="Formato de ID de cliente no válido.")
        
        # Verificar si el cliente existe
        client = clients_collection.find_one({"_id": ObjectId(client_id)})
        if client is None:
            logger.warning("Cliente no encontrado con ID: %s", client_id)
            raise HTTPException(status_code=404, detail="Cliente no encontrado.")
        
        # Retornar el historial de consumo de puntos
        consumption_history = client.get('points_consumption_history', [])
        return consumption_history

    except HTTPException as http_ex:
        logger.error("HTTP Exception: %s", http_ex.detail)
        raise http_ex  # Re-lanzar excepciones HTTP
    except Exception as e:
        logger.error("Error inesperado al obtener el historial de consumo de puntos: %s", e)
        raise HTTPException(status_code=500, detail="Error al obtener el historial de consumo de puntos.")
