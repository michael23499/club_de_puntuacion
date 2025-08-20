from pymongo import MongoClient

# Configura la conexión a MongoDB
MONGODB_URL = "mongodb://localhost:27017/"
client = MongoClient(MONGODB_URL)
db = client["club_puntuacion"]

# Ejecutar los scripts de inserción
def run_scripts():
    import subprocess
    import os

    # Define la carpeta que contiene los scripts
    scripts_folder = "tests"

    # Lista de scripts a ejecutar
    scripts = [
        "test_clients.py",
        "test_establishments.py",
        "test_sponsor.py",
        "test_admin.py"
    ]

    for script in scripts:
        script_path = os.path.join(scripts_folder, script)
        print(f"Ejecutando {script_path}...")
        subprocess.run(["pytest", script_path], check=True)

if __name__ == "__main__":
    run_scripts()
    print("Datos iniciales insertados correctamente.")
