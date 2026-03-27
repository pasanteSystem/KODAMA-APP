import sqlite3
import random
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # IMPORTANTE: Esto es la llave

app = FastAPI()

# Abrimos la puerta para que el HTML pueda hablar con Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def preparar_libro():
    conexion = sqlite3.connect("biblioteca_kodama.db")
    cursor = conexion.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS ecos (contenido TEXT)")
    conexion.commit()
    conexion.close()

preparar_libro()

@app.get("/susurrar/{secreto}")
def susurrar(secreto: str):
    conexion = sqlite3.connect("biblioteca_kodama.db")
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO ecos VALUES (?)", (secreto,))
    conexion.commit()
    cursor.execute("SELECT contenido FROM ecos")
    todos_los_ecos = cursor.fetchall()
    
    if len(todos_los_ecos) > 1:
        # Elegimos uno que NO sea el que acabamos de meter
        eco_elegido = random.choice(todos_los_ecos[:-1])[0]
    else:
        eco_elegido = "El bosque está en silencio... por ahora."
    
    conexion.close()
    return {"el_eco_te_dice": eco_elegido}


# Esto sirve para que cuando entres a la app, se vea tu diseño
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def leer_index():
    return FileResponse("static/index.html")