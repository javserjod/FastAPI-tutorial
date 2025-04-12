from fastapi import APIRouter        #trabaja como router dentro de api principal (main)
# router en vez de fastapi


router = APIRouter(prefix="/products",
                   tags = ["products"],
                   responses={404: {"message": "No encontrado"}})
# Usar el prefijo para un path por defecto. 
# Con tags sale separado de default en swagger


products_list = ["Producto 1", "Producto 2", "Producto 3"]

@router.get("/")
async def products():
    return products_list

@router.get("/{id}")
async def products(id:int):
    return products_list[id]