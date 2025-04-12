from fastapi import FastAPI
from routers import products, users, basic_auth_users, jwt_auth_users, users_db   # otras APIs
from fastapi.staticfiles import StaticFiles    # para representar recursos estáticos

app = FastAPI()

# nuestro API principal es main. Users y products trabajan dentro de main
# lanzar con uvicorn solo este fichero, y los demás se vinculan solos

# Routers -> importar
app.include_router(products.router)
app.include_router(users.router)

app.include_router(basic_auth_users.router)
app.include_router(jwt_auth_users.router)

app.include_router(users_db.router)

# recursos estáticos -> escribir en navegador el path a la imagen
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return "Mi primer server"


# INICIAR SERVER: uvicorn main:app --reload
#           siendo main el nombre del archivo y app el nombre de la instancia FastAPI

# DETENER SERVER: Ctrl + C



