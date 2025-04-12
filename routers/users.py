from fastapi import APIRouter, HTTPException
from pydantic import BaseModel          # PERMITE CREAR UNA ENTIDAD que es transofrma a JSON automáticamente

router = APIRouter(tags = ["user(s)"])

# fastAPI trabaja con type hint !

# GRACIAS A BASEMODEL NO NECESITAMOS NI CONSTRUCTOR
class User(BaseModel):
    id:int
    name:str
    surname:str
    age:int
    

users_list =   [User(id=1, name="Javier", surname="Serrano", age=24),
                User(id=2, name="Zoro", surname="Roronoa", age=19),
                User(id=3, name="Rudeus", surname="Greyrat", age=16),
                User(id=4, name="Jingwoo", surname="Sung", age=23)]


# esto no es óptimo
@router.get("/usersjson")
async def usersjson():
    return [{"name": "Javier", "surname": "Serrano", "age":24}, 
            {"name": "Zoro", "surname": "Roronoa", "age":19},
            {"name": "Rudeus", "surname": "Greyrat", "age":16},
            {"name": "Jingwoo", "surname": "Sung", "age":23}]


def search_user(id:int):
    users = filter(lambda user: user.id == id, users_list)
    try:
        return list(users)[0]
    except:
        return {"error": "No se ha encontrado el usuario"}
    
# pasar parámetro por el PATH
#    usar cuando se cree obligatorio, fijo
@router.get("/user/{id}")
async def user(id:int):
    return search_user(id)

# o pasar parámetro por la QUERY   --> ?param=valor
#    usar cuando parámetro es opcional. Ej: indicar número de usuarios a devolver
@router.get("/user/")
async def user(id:int):
    return search_user(id)


@router.get("/users/")
async def users():
    return users_list


# MÉTODO HTTP POST
# se pasa en el body del mensaje una estructura JSON igual al objeto User, y fastAPI lo interpreta solo
@router.post("/user/", status_code=201, response_model=User)  # response model se muestra en swagger
async def user(user:User):
    # en realidad se trabajaría con bases de datos
    # y con comprobaciones (duplicado, NaN...)
    if not type(search_user(user.id)) == User:
        users_list.append(user)
        return user         # opcional, para no retornar null y retornar usuario                                
    else:
        raise HTTPException(status_code=204, detail="ID ya existente")  # usar raise: si usamos return devuelve como body y no como header
        # return {"error": "ID ya existente"}       ya lo hacemos arriba

                                    
# MÉTODO HTTP PUT
# ejemplo de actualizar usuario
@router.put("/user/")
async def user(user:User):
    for index, saved_user in enumerate(users_list):
        if saved_user.id == user.id:
            users_list[index] = user
            return user

        
        
        
# MÉTODO HTTP DELETE
# ejemplo de borrar usuario por id       
@router.delete("/user/{id}")
async def user(id:int):
    for index, saved_user in enumerate(users_list):
        if saved_user.id == id:
            del users_list[index]
            return users_list
        
    return {"error": "ID no existente"}