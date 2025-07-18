from fastapi import APIRouter, HTTPException, status, Depends, Path
from typing import List
from bd.mono_client import Connection
from models.appointments import UserAppointmentsResponse
from security.auth import get_current_user

router = APIRouter()
appointments_db = Connection(collection_name="Appointments")

@router.get(
    "/CITAS_RESERVADAS/{id}",
    response_model=List[UserAppointmentsResponse],
    status_code=status.HTTP_200_OK,
    summary="Ver citas reservadas del usuario",
    tags=["Citas"]
)
def get_user_appointments(
    id: str = Path(..., description="ID del usuario"),
    current_user: dict = Depends(get_current_user)
):
    """
    Devuelve las citas reservadas del usuario autenticado.
    """
    try:
        # Verificación de seguridad: El usuario solo puede ver sus propias citas
        if id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver estas citas."
            )
        
        # Consulta las citas en la base de datos
        filter_query = {"id_usuario": id}
        citas = appointments_db.read_data(filter_query)

        if not citas:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado o sin citas registradas."
            )

        return citas

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener citas: {e}"
        )
