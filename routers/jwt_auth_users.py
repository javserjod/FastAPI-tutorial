from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# importar del módulo de seguridad, la parte encargada de la autenticación y la forma en la que se recoge y envía usuario y contraseña desde cliente a backend 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

# algoritmo de encriptación de JWT
ALGORITHM = "HS256"

# duración del token generado en caso de autenticación
ACCESS_TOKEN_DURATION = 1           # minutos

# semilla para mejorar encriptación
SECRET = "ugh39g83843g0q8q3u9wg29084yt67671nfg"


router = APIRouter(tags = ["jwt_auth_users"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

# Ahora con criptografía: token y sistema de autenticación mucho más seguro
# JWT -> JSON Web Token
# instalar python-jose
# y passlib (contiene el algoritmo de encriptación bcrypt)

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])      # algoritmo de encriptación para la CONTRASEÑA

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
        "password": "$2a$12$Y9jwop/Tes4hlDj2.3B0fu26c7I6i9WI9xlOHfM2FqA6DXrNzX7me"   # contraseña ENCRIPTADA (usando algoritmo de hasheo, bcrypt en este caso)
    },
    "mouredev2":{
        "username":"mouredev2",
        "full_name":"Brais Moure 2",
        "email":"braismoure2@mourede.com",
        "disabled": True,
        "password": "$2a$12$.tytiyQqVDxXUKyUyA7YLOfcE1nHD.o7MgjMj8mVv6/dG0Ynw4V5a"
    },
}

def search_user_db(username:str):  # crea usuario de tipo UserDB
    if username in users_db:
        return UserDB(**users_db[username])  # indicando con ** que ahí van varios parámetros

def search_user(username:str):  # crea usuario de tipo User
    if username in users_db:
        return User(**users_db[username])  # indicando con ** que ahí van varios parámetros

async def auth_user(token:str = Depends(oauth2)):
    # el token hay que desencriptarlo, para poder exrtaer el usuario (en /users/me se devuelve el usuario propio)
    exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Credenciales de autenticación inválidas",
                            headers={"WWW-Authenticate": "Bearer"})
    try:
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")  # parámetro sub del token
        if username is None:   # si sub vacío
            raise exception

    except JWTError:   # si error en decodificación
        raise exception
    
    # si se llega aquí, se tiene el nombre del usuario
    return search_user(username)


# criterio de dependencia (el token ya no es solo el nombre del usuario sin encriptar, como en el ejemplo anterior)
async def current_user(user:User = Depends(auth_user)):
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
    
    # hay que encriptar la password introducida por el usuario en el form para  poder comparar
    if not crypt.verify(form.password, user.password):   
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña no es correcta")
    
    # generar también access token seguro
    # duración del token (en constante ACCESS_TOKEN_DURATION)
    

    # JWT (Ver en documentación)
    access_token = {"sub": user.username,
                    "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_DURATION), 
                    }
    
    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), 
            "token_type": "bearer"}

    # el access token pasa a ser una sola string encriptada
    
    
@router.get("/users/me")
async def me(user: User = Depends(current_user)):   # agregar criterio de dependencia = tener token
    return user

# no va lo del tiempo...