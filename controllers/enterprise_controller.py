from fastapi import APIRouter, HTTPException, status
from models import Empresa, Categoria # Importa ambos modelos
from bd import get_empresa_collection, get_categoria_collection # Importa las funciones de colección

router = APIRouter()

@router.post("/REGISTRAR_EMPRESA", response_model=Empresa, status_code=status.HTTP_201_CREATED)
async def registrar_empresa(empresa: Empresa):
    empresa_collection = get_empresa_collection()
    categoria_collection = get_categoria_collection()

    # 1. Validar si la categoría existe en MongoDB
    # Buscar por el campo 'id' de la categoría
    categoria_db = await categoria_collection.find_one({"id": empresa.categoria})
    if not categoria_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"status": 404, "error": f"La categoría con id {empresa.categoria} no existe"}
        )

    # 2. Validar duplicados por ID de empresa en MongoDB
    # Buscar por el campo 'id' de la empresa
    empresa_existente = await empresa_collection.find_one({"id": empresa.id})
    if empresa_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"status": 409, "error": "La empresa con el id a registrar ya existe"}
        )

    # 3. Insertar la nueva empresa en MongoDB
    # Convertir el modelo Pydantic a un diccionario para MongoDB
    empresa_dict = empresa.model_dump(by_alias=True) # Usa model_dump() para Pydantic v2+

    # MongoDB normalmente usa '_id' como clave primaria, pero si tu 'id' es único
    # y lo quieres usar como la clave principal de tu documento, puedes hacer:
    # empresa_dict["_id"] = empresa_dict.pop("id") # Opcional, si quieres que tu 'id' sea el '_id' de Mongo

    result = await empresa_collection.insert_one(empresa_dict)

    # Opcional: Puedes verificar result.inserted_id si quieres asegurarte de la inserción
    # Y recuperar el documento recién insertado si necesitas más detalles
    # new_empresa = await empresa_collection.find_one({"_id": result.inserted_id})
    # return new_empresa # Si decides devolver el documento de MongoDB con '_id'

    return empresa # Devolvemos el modelo original que recibimos