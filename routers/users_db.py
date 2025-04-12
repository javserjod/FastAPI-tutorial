# users.py pero empleando base de datos en vez de lista


from fastapi import APIRouter, HTTPException, status

# BaseModel y clase creada en carpeta models
from db.models.user import User

# Schemas
from db.schemas.user import user_schema, users_schema

from db.client import db_client

from bson import ObjectId    #para conseguir objetos con ids en MongoDB

router = APIRouter(prefix="/userdb",
                   tags = ["userdb"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

    

# ahora se hace genérica, pasando clave y valor de criterio de búsqueda
def search_user(field:str, key):   # key de cualquier tipo (a veces vienen str, otras objects)
    try:
        user = user_schema(db_client.users.find_one({field:key}))
        return User(**user)
    except:
        return {"error": "No se ha encontrado el usuario"}
    

    
# pasar parámetro por el PATH
#    usar cuando se cree obligatorio, fijo
@router.get("/{id}")
async def user(id:str):
    return search_user("_id", ObjectId(id))

# # o pasar parámetro por la QUERY   --> ?param=valor
# #    usar cuando parámetro es opcional. Ej: indicar número de usuarios a devolver
# @router.get("/")
# async def user(id:str):
#     return search_user("_id", ObjectId(id))


@router.get("/", response_model=list[User])  # devolver lista de User
async def users():
    return users_schema(db_client.users.find())


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=User)  # response model se muestra en swagger
async def user(user:User):
    if not type(search_user("email", user.email)) == User:
        
        user_dict = dict(user)
        del user_dict["id"]  # ya lo autogenera MongoDB
        
        #crear esquema de BD llamado users y usar método (se crea si no existe). PASAR DICCIONARIO
        #colateralmente, conseguir id autoasignado (con inserted_id)
        id = db_client.users.insert_one(user_dict).inserted_id
        
        # criterio búsqueda: id. MongoDB usa guion bajo. Se retorna un objeto de BBDD...
        # Nuevo concepto: schemas (ver su carpeta)
        # Una cosa son los modelos y otra el cómo se tratan en BBDD
        # Transformar objeto de BBDD a diccionario según modelo con schema correspondiente
        new_user = user_schema(db_client.users.find_one({"_id":id}))
        # O sea, schema ajusta lo devuelto por BBDD a un modelo
        
        return User(**new_user)     # objeto User
    else:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Email ya existente")  # usar raise: si usamos return devuelve como body y no como header
        # return {"error": "ID ya existente"}       ya lo hacemos arriba

                                    
# MÉTODO HTTP PUT
# ejemplo de actualizar usuario
@router.put("/", response_model=User)
async def user(user:User):
    user_dict = dict(user)
    del user_dict["id"]
    try:
        db_client.users.find_one_and_replace({"_id": ObjectId(user.id)}, user_dict)
    except:
        return {"error":"No se ha actualizado el usuario"}
    
    return search_user("_id", ObjectId(user.id))
        
        
# MÉTODO HTTP DELETE
# ejemplo de borrar usuario por id       
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT,)
async def user(id:str):
    
    found = db_client.users.find_one_and_delete({"_id":ObjectId(id)})
    
    if not found:
        return {"error": "No se ha eliminado el usuario"}