from datetime import datetime
from pydantic import BaseModel, EmailStr
from bson import ObjectId
from typing import List, Optional

class Transaction(BaseModel):
    """
    Modelo que representa una transacción realizada por un cliente.

    Attributes:
        establishment_id (str): ID del establecimiento donde se realizó la transacción.
        points (int): Puntos ganados en la transacción.
        description (str): Descripción de la transacción.
        amount_spent (float): Monto gastado en la transacción.
    """
    establishment_id: str
    points: int  # Puntos ganados
    description: str
    amount_spent: float  # Monto gastado en la transacción

class PointsConsumption(BaseModel):
    """
    Modelo que representa el consumo de puntos.

    Attributes:
        points_consumed (int): Puntos gastados (valor negativo).
        description (str): Descripción del uso de los puntos.
        date (str): Fecha del consumo.
        expiration_date (str): Fecha de expiración de los puntos consumidos.
    """
    points_consumed: int  # Puntos gastados (valor negativo)
    description: str  # Descripción del uso de los puntos
    date: str  # Fecha del consumo
    expiration_date: str  # Fecha de expiración

class Client(BaseModel):
    """
    Modelo que representa a un cliente.

    Attributes:
        id (Optional[str]): ID del cliente, opcional.
        name (str): Nombre del cliente.
        email (EmailStr): Correo electrónico del cliente.
        password (str): Contraseña del cliente.
        points (Optional[int]): Puntos acumulados, por defecto 0.
        role (str): Rol del cliente, por defecto "client".
        transaction_history (List[Transaction]): Historial de transacciones del cliente.
        points_consumption_history (List[PointsConsumption]): Historial de consumo de puntos.
    """
    id: Optional[str] = None  # Agregar campo id como opcional
    name: str
    email: EmailStr  # Usar EmailStr para validar el correo electrónico
    password: str  # Agregar campo para la contraseña
    points: Optional[int] = 0  # Puntos acumulados
    role: str = "client"  # Rol por defecto para los clientes
    transaction_history: List[Transaction] = []  # Historial de transacciones
    points_consumption_history: List[PointsConsumption] = []  # Historial de consumo de puntos

    class Config:
        json_encoders = {
            ObjectId: str  # Convertir ObjectId a string al serializar a JSON
        }

class Establishment(BaseModel):
    """
    Modelo que representa un establecimiento.

    Attributes:
        id (Optional[str]): ID del establecimiento, opcional.
        name (str): Nombre del establecimiento.
        location (str): Ubicación del establecimiento.
        role (str): Rol del establecimiento (ej. "establishment").
        email (str): Correo electrónico del establecimiento.
        password (str): Contraseña del establecimiento.
    """
    id: Optional[str] = None  # Agregar campo id como opcional
    name: str
    location: str
    role: str  # Rol del establecimiento
    email: str  # Agregar correo electrónico
    password: str  # Agregar contraseña

class EstablishmentCreate(BaseModel):
    """
    Modelo para crear un nuevo establecimiento.

    Attributes:
        name (str): Nombre del establecimiento.
        location (str): Ubicación del establecimiento.
        email (str): Correo electrónico del establecimiento.
        password (str): Contraseña del establecimiento.
    """
    name: str
    location: str
    email: str  # Agregar correo electrónico
    password: str  # Agregar contraseña

class RedeemPointsRequest(BaseModel):
    """
    Modelo para solicitar la redención de puntos.

    Attributes:
        points (int): Cantidad de puntos a redimir.
        description (str): Descripción de la redención.
    """
    points: int  # Cantidad de puntos a redimir
    description: str  # Descripción de la redención

class Administrator(BaseModel):
    """
    Modelo que representa a un administrador.

    Attributes:
        name (str): Nombre del administrador.
        email (str): Correo electrónico del administrador.
        password (str): Contraseña del administrador.
        role (str): Rol del administrador, por defecto "administrator".
    """
    name: str
    email: str
    password: str
    role: str = "administrator"  # Rol por defecto para los administradores

class Sponsor(BaseModel):
    """
    Modelo que representa a un patrocinador.

    Attributes:
        name (str): Nombre del patrocinador.
        email (str): Correo electrónico del patrocinador.
        password (str): Contraseña del patrocinador.
        role (str): Rol del patrocinador, por defecto "sponsor".
    """
    name: str
    email: str
    password: str
    role: str = "sponsor"  # Rol por defecto para los patrocinadores

class PointsPolicy(BaseModel):
    """
    Modelo que representa la política de puntos.

    Attributes:
        min_points (int): Mínimo de puntos permitidos.
        max_points (int): Máximo de puntos permitidos.
        expiration_days (int): Días hasta que los puntos expiran.
    """
    min_points: int  # Mínimo de puntos permitidos
    max_points: int  # Máximo de puntos permitidos
    expiration_days: int  # Días hasta que los puntos expiran

class PointsAssignment(BaseModel):
    """
    Modelo que representa la asignación de puntos.

    Attributes:
        points (int): Cantidad de puntos asignados.
        reason (str): Razón de la asignación de puntos, opcional.
        date (Optional[datetime]): Fecha de la asignación de puntos, opcional.
    """
    points: int  # Cantidad de puntos asignados
    reason: str = None  # Razón de la asignación de puntos
    date: Optional[datetime] = None  # Fecha de la asignación de puntos

class PointsResponse(BaseModel):
    """
    Modelo que representa la respuesta al consultar puntos.

    Attributes:
        points (int): Cantidad de puntos.
        message (str): Mensaje relacionado con la consulta.
    """
    points: int  # Cantidad de puntos
    message: str  # Mensaje relacionado con la consulta
