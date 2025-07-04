# controllers/enterprise.py
from fastapi import APIRouter, HTTPException, Path, status
from bd.mono_client import Connection
from models.enterprise import Enterprise

router = APIRouter()
enterprise_db = Connection(collection_name="Enterprise")

enterprise_example = {
    "id_empresa": "68674b8ef6585d5be64e81c3",
    "nombre_empresa": "Ejemplo S.A.",
    "categoria": "Tecnología",
    "informacion_empresa": "Empresa dedicada al desarrollo de software.",
    "horario": "Lunes a Viernes de 8am a 5pm",
    "telefono": "+506 8888 8888",
    "correo_electronico": "info@ejemplo.com",
    "direccion": "Calle 123, San José, Costa Rica",
    "tipo_cedula": "física",
    "numero_cedula": "3007001010"
}

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