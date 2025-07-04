from pydantic import BaseModel, Field
from typing import Literal, Optional

class Enterprise(BaseModel):
    id: str
    tipo_id: Literal["física", "jurídica"]
    nombre_empresa: str
    direccion: str
    categoria: str
    correo_electronico: str
    telefono: str
    fotos: Optional[str] = None
    horario: Optional[str] = None
    informacion_empresa: Optional[str] = Field(None, alias="Información de la empresa ")
    contrasena: str = Field(..., alias="Contraseña")