from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.models import Client, Establishment, Administrator, Sponsor
from app.database import (
    clients_collection,
    establishments_collection,
    administrators_collection,
    sponsors_collection
)

# Configuración de JWT https://jwtsecrets.com/ - api key
SECRET_KEY = "eMCTi0OJcfIpp+92U3EUCafYoiac4jGVI4Hb/0VocUkdFr3NFHh2/8oI1X/Xh5VQ"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Inicialización de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si la contraseña en texto plano coincide con la contraseña hasheada.

    Args:
        plain_password (str): Contraseña en texto plano.
        hashed_password (str): Contraseña hasheada.

    Returns:
        bool: True si coincide, False de lo contrario.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Genera un hash para la contraseña proporcionada.

    Args:
        password (str): Contraseña en texto plano.

    Returns:
        str: Contraseña hasheada.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Crea un token de acceso JWT.

    Args:
        data (dict): Datos a incluir en el token.
        expires_delta (timedelta, optional): Tiempo adicional para la expiración del token.

    Returns:
        str: Token de acceso JWT.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Client | Establishment | Administrator | Sponsor:
    """
    Obtiene el usuario actual a partir del token JWT proporcionado.

    Args:
        token (str): Token JWT.

    Returns:
        Client | Establishment | Administrator | Sponsor: El usuario autenticado.

    Raises:
        HTTPException: Si las credenciales no son válidas.
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Verificar el tipo de usuario
    user = clients_collection.find_one({"email": email}) or \
           establishments_collection.find_one({"email": email}) or \
           administrators_collection.find_one({"email": email}) or \
           sponsors_collection.find_one({"email": email})

    if user is None:
        raise credentials_exception

    # Asegurarse de que el campo points_consumption_history esté presente
    if 'points_consumption_history' not in user:
        user['points_consumption_history'] = []  # Inicializar como lista vacía si no existe

    # Asignar el ID del usuario al modelo correspondiente
    user['id'] = str(user['_id'])  # Asegúrate de que el id se asigne correctamente

    if 'role' in user:
        if user['role'] == 'client':
            return Client(**user)
        elif user['role'] == 'establishment':
            return Establishment(**user)
        elif user['role'] == 'administrator':
            return Administrator(**user)
        elif user['role'] == 'sponsor':
            return Sponsor(**user)
    
    raise credentials_exception

def role_required(role: str):
    """
    Decorador para verificar si el usuario tiene el rol requerido.

    Args:
        role (str): Rol que se requiere para acceder a la ruta.

    Returns:
        function: Función que verifica el rol del usuario.
    """
    def role_checker(user: Client | Establishment | Administrator | Sponsor = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(status_code=403, detail="Access denied")
    return role_checker
