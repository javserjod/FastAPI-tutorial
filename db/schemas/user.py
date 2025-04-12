# Transformar lo que viene de BBDD a lo que espera el programa (objeto User)



def user_schema(user) -> dict:
    return {
        "id": str(user["_id"]),   # Viene como objeto, transformar a str porque así lo dice el modelo
        "username": user["username"],
        "email": user["email"]
    }


# devolver lista de varios
def users_schema(users) -> list:
    return [user_schema(user) for user in users]