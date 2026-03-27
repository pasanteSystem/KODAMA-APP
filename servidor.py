import sqlite3
import random
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 1. Configuración de CORS completa
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, # Añadimos esto para mayor compatibilidad
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Aseguramos la ruta de la base de datos
DB_PATH = os.path.join(os.getcwd(), "biblioteca_kodama.db")

def preparar_libro():
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS ecos (contenido TEXT)")
    conexion.commit()
    conexion.close()

preparar_libro()

@app.get("/susurrar/{secreto}")
def susurrar(secreto: str):
    try:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        
        # Guardar el nuevo secreto
        cursor.execute("INSERT INTO ecos VALUES (?)", (secreto,))
        conexion.commit()
        
        # Obtener todos para el eco
        cursor.execute("SELECT contenido FROM ecos")
        #fetchall devuelve una lista de tuplas [('texto1',), ('texto2',)]
        todos_los_ecos = [fila[0] for fila in cursor.fetchall()]
        
        if len(todos_los_ecos) > 1:
            # Filtramos para no devolver el mismo que acaba de entrar
            otros_ecos = [e for e in todos_los_ecos if e != secreto]
            if otros_ecos:
                eco_elegido = random.choice(otros_ecos)
            else:
                eco_elegido = random.choice(todos_los_ecos)
        else:
            eco_elegido = "El bosque está en silencio... eres el primer susurro."
        
        conexion.close()
        return {"el_eco_te_dice": eco_elegido}
    except Exception as e:
        print(f"Error en el servidor: {e}")
        return {"el_eco_te_dice": "El eco se perdió en la niebla... (Error de base de datos)"}

# Montar estáticos y ruta principal
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def leer_index():
    return FileResponse("static/index.html")