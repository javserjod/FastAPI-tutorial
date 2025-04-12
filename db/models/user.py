from pydantic import BaseModel
from typing import Optional

    

class User(BaseModel):
    id: Optional[str] = None      # OPCIONAL PORQUE MONGODB YA AÑADE IDENTIFICADOR ÚNICO (y str)      
    username:str
    email:str