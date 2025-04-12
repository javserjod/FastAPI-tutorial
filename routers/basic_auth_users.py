from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# importar del módulo de seguridad, la parte encargada de la autenticación y la forma en la que se recoge y envía usuario y contraseña desde cliente a backend 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(tags = ["basic_auth_users"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

# usuario con el que se trabaja en red
class User(BaseModel):   # esta entidad va a través de la red (por eso no lleva contraseña)
    username:str
    full_name:str
    email:str
    disabled:bool

# usuario de base de datos
class UserDB(User):
    password:str

    
users_db = {
    "mouredev":{
        "username":"mouredev",
        "full_name":"Brais Moure",
        "email":"braismoure@mourede.com",
        "disabled": False,
        "password": "123456"   # password iría hasheado
    },
    "mouredev2":{
        "username":"mouredev2",
        "full_name":"Brais Moure 2",
        "email":"braismoure2@mourede.com",
        "disabled": True,
        "password": "654321"
    },
}

def search_user_db(username:str):  # crea usuario de tipo UserDB
    if username in users_db:
        return UserDB(**users_db[username])  # indicando con ** que ahí van varios parámetros
    
def search_user(username:str):  # crea usuario de tipo User
    if username in users_db:
        return User(**users_db[username])  # indicando con ** que ahí van varios parámetros
    

# criterio de dependencia -> comprueba token en bearer
async def current_user(token:str = Depends(oauth2)):
    user = search_user(token)
    if not user: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Credenciales de autenticación inválidas",
                            headers={"WWW-Authenticate": "Bearer"})
    if user.disabled:   # si disabled, aunque ya se haya autenticado, no permitir acceso
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Usuario desactivado")
    
    return user  # debe devolverse usuario de tipo User (no UserDB, que lleva la contraseña)


    
@router.post("/login")  # dirección indicada en la instancia de OAuth2
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario no es correcto")
    
    user = search_user_db(form.username)  # crear instancia UserDB (lleva la password)
    if not form.password == user.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña no es correcta")
    
    # si hay éxito, devolver access token (en realidad debería ser desconocido y encriptado)  
    return {"access_token": user.username, "token_type": "bearer"}



@router.get("/users/me")
async def me(user: User = Depends(current_user)):   # agregar criterio de dependencia = tener token
    return user



# Autenticación OAuth2 es muy simple, y aquí no se ha usado encriptación