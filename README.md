# README

## Instalación

Para instalar las dependencias necesarias para ejecutar este proyecto, asegúrate de tener **Python 3.7** o superior instalado en tu sistema. Luego, sigue estos pasos:

### 1. Crear un Entorno Virtual

Ejecuta el siguiente comando en tu terminal para crear un entorno virtual:

```bash
python -m venv backendtestenv
```

### 2. Activar el Entorno Virtual Esto creará un entorno virtual llamado backendtestenv, procedemos activarlo con el siguiente comando en la terminal:

Windows:
`.\venv\backendtestenv\Scripts\activate`
En macOS y Linux:
`source backendtestenv/bin/activate`

### 3. Instalar las Dependencias

Una vez que el entorno virtual esté activado, instala todas las dependencias necesarias ejecutando el siguiente comando:

`pip install -r requirements.txt`

Esto instalará las siguientes bibliotecas:
fastapi: Framework web para construir APIs.
uvicorn: Servidor ASGI para ejecutar aplicaciones FastAPI.
pydantic: Para la validación de datos y configuración.
motor: Controlador asíncrono para MongoDB.
python-jose: Para la creación y verificación de tokens JWT.
passlib[bcrypt]: Para el manejo seguro de contraseñas.
python-multipart: Para manejar formularios multipart en FastAPI.
wheel: Para la construcción de paquetes.
pytest: Framework para pruebas.
httpx: Cliente HTTP asíncrono.
pymongo: Para la interacción con MongoDB.
bcrypt: Para el manejo seguro de contraseñas.
email_validator: Para la validación de correos electrónicos.
pytest-asyncio: Para pruebas asíncronas.

### 4. Verificar la Instalación

Verifica que todas las bibliotecas se hayan instalado correctamente con el comando:
`pip list`

Si falta alguna, puedes instalarla ejecutando:
`pip install <nombre_de_la_biblioteca>`

### 5. Ejecutar la Aplicación

Después de instalar las dependencias, ejecuta la aplicación utilizando el siguiente comando:
`uvicorn main:app --reload`

Esto iniciará el servidor de desarrollo, y podrás acceder a la API en http://127.0.0.1:8000. También se puede acceder a la documentación de Swagger UI en: http://127.0.0.1:8000/docs#/. Se recomienda activar la autorización del SwaggerUI utilizando OAuth2PasswordBearer (OAuth2, password) con el nombre de usuario y contraseña de un establecimiento registrado en la base de datos (Insertar datos iniciales con el script asignado en la línea 77).

La documentación de todas las APIs estan en Swagger UI que se generaron automáticamente en fastapi, se pueden ver en el docs local: http://127.0.0.1:8000/docs#/

## Configuración de la Base de Datos

La aplicación utiliza MongoDB como base de datos, asi que debemos tenerlo instalado podemos verificar si esta correctamente instalado viendo su version con el siguiente comando: `mongod --version`.
La configuración de la conexión se realiza en el archivo `database.py`. A continuación se presentan los detalles de configuración:

- **URL de Conexión**:

```python
MONGODB_URL = "mongodb://localhost:27017/"
NAME = "club_de_puntos"
Base de Datos:
La base de datos utilizada es club_puntuacion. Esta base de datos se crea automáticamente cuando se inserta el primer documento en cualquiera de sus colecciones.
```

### Ejemplo de Inserciones Iniciales (Datos iniciales)

Para facilitar la configuración y prueba de la aplicación, puedes utilizar el siguiente script para insertar datos iniciales en la base de datos `club_puntuacion`. Este script ejecutará los archivos de prueba que ya he creado.

Script: **`python insert_initial_data.py`**

### Ejemplo de Uso de endpoints para Clients - Recomendable usar Postman es donde he probado todas y cada una de las APIs

### 1. Registro de Cliente

**Endpoint:** `POST /clients/register/`
**Descripción:** Registra un nuevo cliente en la base de datos.
**Ejemplo de Solicitud:**

```json
{
  "name": "Michael",
  "email": "michael@gmail.com",
  "password": "securepassword",
  "points": 0
}
```

**Ejemplo de Respuesta:**

```json
{
  "id": "68a55151b94e58b6f260fd5b",
  "name": "Michael",
  "email": "michael@gmail.com",
  "password": "$2b$12$2iHho2xnYi2c7yfhaCrW1ukwd699109YW3jR11nvmgSKgyJEREsKO",
  "points": 0,
  "role": "client",
  "transaction_history": [],
  "points_consumption_history": []
}
```

### 2. Inicio de Sesión de Cliente

**Endpoint:** `POST /clients/login/`
**Descripción:** Inicia sesión de un cliente y genera un token de acceso.
**Ejemplo de Solicitud:**

```x-www-form-urlencoded
{
    "username": "michael@gmail.com",
    "password": "securepassword"
}
```

**Ejemplo de Respuesta:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtaWNoYWVsQGdtYWlsLmNvbSIsImV4cCI6MTc1NTY2Nzg3M30.-MFSW4EktPuzbroOM8x4zktMRqPwAmHovDdVBgcwotk",
  "token_type": "bearer"
}
```

### 3. Obtener información del cliente

**Endpoint:** `GET /clients/{client_id}`
**Descripción:** Obtiene la información de un cliente específico..
**Ejemplo de Solicitud:**
`GET /clients/68a55151b94e58b6f260fd5b/`
Headers:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtaWNoYWVsQGdtYWlsLmNvbSIsImV4cCI6MTc1NTY2OTAzNn0.KfGKpZ8XBnUR3tb82zmeKe3_4Cx-cDUaJs-3syTT42Q

**Ejemplo de Respuesta:**

```json
{
  "id": "68a55151b94e58b6f260fd5b",
  "name": "Michael",
  "email": "michael@gmail.com",
  "password": "$2b$12$2iHho2xnYi2c7yfhaCrW1ukwd699109YW3jR11nvmgSKgyJEREsKO",
  "points": 0,
  "role": "client",
  "transaction_history": [],
  "points_consumption_history": []
}
```

### 4. Consulta de cantidad de puntos del cliente

**Endpoint:** `GET /clients/{client_id}/points/`

**Descripción:** Obtiene la cantidad de puntos de un cliente especifico.

**Ejemplo de Solicitud:**
GET /clients/68a55151b94e58b6f260fd5b/points/
Headers:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtaWNoYWVsQGdtYWlsLmNvbSIsImV4cCI6MTc1NTY2OTAzNn0.KfGKpZ8XBnUR3tb82zmeKe3_4Cx-cDUaJs-3syTT42Q

**Ejemplo de Respuesta:**

```json
{
  "points": 150,
  "message": "Este cliente posee 150 puntos."
}
```

### 5. Registrar una Transacción de un cliente

**Endpoint:** `POST /clients/{client_id}/transactions/`

**Descripción:** Registra una nueva transacción para un cliente.

**Ejemplo de Solicitud:**

```json
{
  "establishment_id": "KFC",
  "points": 0,
  "description": "Hamburguesas",
  "amount_spent": 20.0
}
```

**Ejemplo de Respuesta:**

```json
{
  "establishment_id": "KFC",
  "points": 200,
  "description": "Hamburguesa",
  "amount_spent": 20.0
}
```

### 6. Rescate de puntos

**Endpoint:** `POST /clients/{client_id}/redeem/`

**Descripción:** Redime puntos de un cliente.

**Ejemplo de Solicitud:**

Usando el local podemos usar la siguiente ruta:
http://127.0.0.1:8000/clients/68a55151b94e58b6f260fd5b/redeem/
Headers:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtaWNoYWVsQGdtYWlsLmNvbSIsImV4cCI6MTc1NTY2OTAzNn0.KfGKpZ8XBnUR3tb82zmeKe3_4Cx-cDUaJs-3syTT42Q

```json
{
  "points": 20,
  "description": "Descuento en KFC"
}
```

**Ejemplo de Respuesta:**

```json
{
  "message": "Puntos redimidos con éxito. Gastaste 20 puntos."
}
```

### 7. Obtener Historial de Consumo de Puntos por cliente

**Endpoint:** `GET /clients/{client_id}/points_consumption_history/`

**Descripción:** Obtiene el historial de consumo de puntos de un cliente.

**Ejemplo de Solicitud:**

`GET /clients/68a55151b94e58b6f260fd5b/points_consumption_history/`
Headers:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtaWNoYWVsQGdtYWlsLmNvbSIsImV4cCI6MTc1NTY2OTAzNn0.KfGKpZ8XBnUR3tb82zmeKe3_4Cx-cDUaJs-3syTT42Q
**Ejemplo de Respuesta:**

```json
[
  {
    "points_consumed": -20,
    "description": "Descuento en KFC",
    "date": "20-08-25 01:43",
    "expiration_date": "18-11-25 01:43"
  }
]
```

1. ## Ejemplo de Uso de endpoints para Establishments - Recomendable usar Postman es donde he probado todas y cada una de las apis

### 1. Registro de Establecimiento

**Endpoint:** `POST /establishments/register/`

**Descripción:** Registra un nuevo establecimiento en la base de datos.

**Ejemplo de Solicitud:**

```json
{
  "name": "Mcdonalds",
  "location": "Madrid",
  "email": "anthony@gmail.com",
  "password": "456"
}
```

**Ejemplo de Respuesta:**

```json
{
  "id": "68a56288bfe847f4b225e4dc",
  "name": "Mcdonalds",
  "location": "Madrid",
  "role": "establishment",
  "email": "anthony@gmail.com",
  "password": "$2b$12$HE8r8iaReJK8oSPAS8mrTukfMQ2izFPhLuGN/57fZIfHoR744j2JG"
}
```

### 2. Inicio de Sesión de Establecimiento

**Endpoint:** `POST /establishments/login/`

**Descripción:** Inicia sesión de un establecimiento y genera un token de acceso.

**Ejemplo de Solicitud:**

```x-www-form-urlencoded
{
 "username": "anthony@gmail.com",
 "password": "456"
}
**Ejemplo de Respuesta:**
json
{
 "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9eyJzdWIiOiJhbnRob255QGdtYWlsLmNvbSIsInJvbGUiOiJlc3RhYmxpc2htZW50IiwiZXhwIjoxNzU1NjcxMjAyfQ.iHWWoJuMeW8mqoeA4DwEESmQcYHxE4-7Hq7UB-Mz6TM",
 "token_type": "bearer"
}
```

### 3. Actualizar Política de Puntos

**Endpoint:** `PUT /establishments/{establishment_id}/points-policy/`
establishment_id: 68a56288bfe847f4b225e4dc
Headers:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbnRob255QGdtYWlsLmNvbSIsInJvbGUiOiJlc3RhYmxpc2htZW50IiwiZXhwIjoxNzU1NjcxMjAyfQ.iHWWoJuMeW8mqoeA4DwEESmQcYHxE4-7Hq7UB-Mz6TM

**Descripción:** Actualiza la política de puntos de un establecimiento.

**Ejemplo de Solicitud:**

```json
{
  "min_points": 20,
  "max_points": 200,
  "expiration_days": 30
}
```

**Ejemplo de Respuesta:**

```json
{
  "detail": "Points policy updated successfully"
}
```

### 4. Asignar Puntos a Establecimiento

**Endpoint:** `POST /establishments/{establishment_id}/assign-points/`
establishment_id: 68a56288bfe847f4b225e4dc
Headers:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbnRob255QGdtYWlsLmNvbSIsInJvbGUiOiJlc3RhYmxpc2htZW50IiwiZXhwIjoxNzU1NjcxMjAyfQ.iHWWoJuMeW8mqoeA4DwEESmQcYHxE4-7Hq7UB-Mz6TM

**Descripción:** Asigna puntos a un establecimiento.

**Ejemplo de Solicitud:**

```json
{
  "points": 400,
  "reason": "Promoción especial"
}
```

**Ejemplo de Respuesta:**

```json
{
  "detail": "Points assigned successfully",
  "distribution_record": {
    "points": 400,
    "date": "20-08-25 06:06",
    "reason": "Promoción especial"
  }
}
```

### 5. Obtener Reporte de Uso

**Endpoint:** `GET /establishments/reportes/uso`
Headers:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbnRob255QGdtYWlsLmNvbSIsInJvbGUiOiJlc3RhYmxpc2htZW50IiwiZXhwIjoxNzU1NjcxMjAyfQ.iHWWoJuMeW8mqoeA4DwEESmQcYHxE4-7Hq7UB-Mz6TM

**Descripción:** Obtiene un reporte de uso de puntos para un cliente específico, filtrando por fecha y hora opcionalmente.

**Ejemplo de Solicitud:**
Params:
client_id: 68a55151b94e58b6f260fd5b
fecha: 20-08-25 [opcional]
hora: 01:43 [opcional]

**Ejemplo de Respuesta:**

```json
[
  {
    "points_consumed": -20,
    "description": "Descuento en KFC",
    "date": "20-08-25 01:43",
    "expiration_date": "18-11-25 01:43"
  }
]
```
