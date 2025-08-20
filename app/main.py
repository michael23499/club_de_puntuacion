from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import create_access_token, verify_password  
from app.database import establishments_collection
from app.routes import clients, establishments, admin, sponsor

# Crea una instancia de la aplicación FastAPI
app = FastAPI()

# Incluye los routers de las diferentes rutas en la aplicación
app.include_router(clients.router)        # Rutas para la gestión de clientes
app.include_router(establishments.router)  # Rutas para la gestión de establecimientos
app.include_router(admin.router)           # Rutas para la gestión administrativa
app.include_router(sponsor.router)         # Rutas para la gestión de patrocinadores

# Ruta para obtener el token de acceso
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = establishments_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user['password']):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user['email']})
    return {"access_token": access_token, "token_type": "bearer"}

# Ruta raíz de la API
@app.get("/")
async def root():
    """
    Ruta raíz que devuelve un mensaje de bienvenida a la API REST.
    """
    return {"message": "Welcome to the Club de Puntuación API - Backend Test Full&Fast"}
