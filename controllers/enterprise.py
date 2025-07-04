# controllers/enterprise.py
from fastapi import APIRouter, HTTPException, Path, status
from bd.mono_client import Connection
from models.enterprise import Enterprise

router = APIRouter()
enterprise_db = Connection(collection_name="Enterprise")

enterprise_example = {
    "id_empresa": "68674b8ef6585d5be64e81c3",
    "nombre_empresa": "Ejemplo S.A.",
    "categoria": "Restaurantes",
    "informacion_empresa": "Empresa dedicada al desarrollo de software.",
    "horario": "Lunes a Viernes de 8am a 5pm",
    "telefono": "+506 8888 8888",
    "correo_electronico": "info@ejemplo.com",
    "direccion": "Calle 123, San José, Costa Rica",
    "tipo_cedula": "física",
    "numero_cedula": "3007001010"
}

# Category mapping for display names
CATEGORY_MAPPING = {
    "1": "Restaurantes",
    "2": "Clinicas", 
    "3": "Barberias",
    "4": "Hoteles"
}

# Example response for enterprises by category
enterprises_by_category_example = [
    {
        "id_empresa": "68674b8ef6585d5be64e81c3",
        "nombre_empresa": "Restaurante Ejemplo",
        "categoria": "Restaurantes",
        "informacion_empresa": "Restaurante especializado en comida tradicional.",
        "horario": "Lunes a Domingo de 11am a 10pm",
        "telefono": "+506 8888 8888",
        "correo_electronico": "info@restaurante.com",
        "direccion": "Calle 123, San José, Costa Rica",
        "tipo_cedula": "jurídica",
        "numero_cedula": "3001234567"
    },
    {
        "id_empresa": "68674b8ef6585d5be64e81c4",
        "nombre_empresa": "Restaurante Ejemplo 2",
        "categoria": "Restaurantes", 
        "informacion_empresa": "Restaurante de comida italiana.",
        "horario": "Martes a Domingo de 12pm a 11pm",
        "telefono": "+506 8888 9999",
        "correo_electronico": "info@italiano.com",
        "direccion": "Avenida Central, San José, Costa Rica",
        "tipo_cedula": "jurídica",
        "numero_cedula": "3001234568"
    }
]

@router.get(
    "/EMPRESA_ESPECIFICA/{id}",
    response_model=Enterprise,
    summary="Obtener información de una empresa por ID",
    tags=["Empresas"],
    responses={
        status.HTTP_200_OK: {
            "description": "Respuesta exitosa. Devuelve los detalles de la empresa.",
            "content": {"application/json": {"example": enterprise_example}}
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Error: El formato del ID proporcionado es inválido.",
            "content": {"application/json": {"example": {"detail": "El formato del ID 'id-con-formato-incorrecto' no es válido."}}}
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Error: La empresa con el ID especificado no fue encontrada.",
            "content": {"application/json": {"example": {"detail": "No se encontró un documento con el id '68674b8ef6585d5be64e81c3'."}}}
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Error de Validación: Los datos enviados no son válidos.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["path", "id"],
                                "msg": "El valor proporcionado no es un ObjectId válido.",
                                "type": "validation_error.objectid"
                            }
                        ]
                    }
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Error: Ocurrió un problema inesperado en el servidor.",
            "content": {"application/json": {"example": {"detail": "Ocurrió un error inesperado al consultar la base de datos."}}}
        }
    }
)
def get_enterprise_by_id(
    id: str = Path(
        ...,
        title="ID de la Empresa",
        description="ID único de la empresa a consultar (debe ser un ObjectId de 24 caracteres hexadecimales).",
        example="68674b8ef6585d5be64e81c3"
    )
):
    """
    Obtiene toda la información detallada de una empresa específica
    registrada en el sistema a través de su ID único.
    """
    try:
        enterprise_data = enterprise_db.get_by_id(id)

        response_data = {
            "id_empresa": enterprise_data.get("_id"),
            "nombre_empresa": enterprise_data.get("nombre_empresa"),
            "categoria": enterprise_data.get("categoria"),
            "informacion_empresa": enterprise_data.get("informacion_empresa"),
            "horario": enterprise_data.get("horario"),
            "telefono": enterprise_data.get("telefono"),
            "correo_electronico": enterprise_data.get("correo_electronico"),
            "direccion": enterprise_data.get("direccion"),
            "tipo_cedula": enterprise_data.get("tipo_cedula"),
            "numero_cedula": enterprise_data.get("numero_cedula")
        }

        return response_data

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ha ocurrido un error inesperado en el controlador: {e}"
        )

@router.get(
    "/EMPRESA_FILTRO_POR_CATEGORIA/{id_categoria}",
    summary="Obtener empresas por categoría",
    tags=["Empresas"],
    responses={
        status.HTTP_200_OK: {
            "description": "Respuesta exitosa. Devuelve la lista de empresas de la categoría especificada.",
            "content": {"application/json": {"example": enterprises_by_category_example}}
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Error: ID de categoría inválido.",
            "content": {"application/json": {"example": {"detail": "ID de categoría '999' no es válido. Use: 1=Restaurantes, 2=Clinicas, 3=Barberias, 4=Hoteles"}}}
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No se encontraron empresas en esta categoría.",
            "content": {"application/json": {"example": {"detail": "No se encontraron empresas en la categoría 'Restaurantes'"}}}
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Error interno del servidor.",
            "content": {"application/json": {"example": {"detail": "Error inesperado al consultar las empresas"}}}
        }
    }
)
def get_enterprises_by_category(
    id_categoria: str = Path(
        ...,
        title="ID de Categoría",
        description="ID de la categoría de empresa (1=Restaurantes, 2=Clinicas, 3=Barberias, 4=Hoteles)",
        example="1"
    )
):
    """
    Obtiene todas las empresas que pertenecen a una categoría específica.
    
    Categorías disponibles:
    - 1: Restaurantes
    - 2: Clinicas  
    - 3: Barberias
    - 4: Hoteles
    """
    try:
        # Validar que el ID de categoría sea válido
        if id_categoria not in CATEGORY_MAPPING:
            valid_categories = ", ".join([f"{k}={v}" for k, v in CATEGORY_MAPPING.items()])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ID de categoría '{id_categoria}' no es válido. Use: {valid_categories}"
            )

        # Obtener el nombre de la categoría
        category_name = CATEGORY_MAPPING[id_categoria]
        
        # Buscar empresas por categoría
        enterprises_data = enterprise_db.find_many({"categoria": category_name})
        
        # Si no se encuentran empresas, devolver lista vacía
        if not enterprises_data:
            return []
        
        # Formatear respuesta
        response_data = []
        for enterprise in enterprises_data:
            formatted_enterprise = {
                "id_empresa": enterprise.get("_id"),
                "nombre_empresa": enterprise.get("nombre_empresa"),
                "categoria": enterprise.get("categoria"),
                "informacion_empresa": enterprise.get("informacion_empresa"),
                "horario": enterprise.get("horario"),
                "telefono": enterprise.get("telefono"),
                "correo_electronico": enterprise.get("correo_electronico"),
                "direccion": enterprise.get("direccion"),
                "tipo_cedula": enterprise.get("tipo_cedula"),
                "numero_cedula": enterprise.get("numero_cedula")
            }
            response_data.append(formatted_enterprise)
        
        return response_data

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al consultar las empresas: {e}"
        )