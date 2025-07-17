from pydantic import BaseModel, Field
from typing import Optional

class Enterprise(BaseModel):
    # Use Field with alias to map MongoDB's _id to id_empresa
    # Optional because it's not provided on creation, but present on retrieval
    id_empresa: Optional[str] = Field(None, alias="_id")
    nombre_empresa: str
    categoria: str
    informacion_empresa: str
    horario: str
    telefono: str
    correo_electronico: str
    direccion: str
    tipo_cedula: str
    numero_cedula: str

    class Config:
        # Allows Pydantic to populate fields by either field name or alias
        populate_by_name = True
        # Example for Swagger UI
        json_schema_extra = {
            "example": {
                "nombre_empresa": "Example Corp.",
                "categoria": "Restaurants",
                "informacion_empresa": "A company focused on software development.",
                "horario": "Monday to Friday from 8am to 5pm",
                "telefono": "+506 8888 8888",
                "correo_electronico": "info@example.com",
                "direccion": "123 Street, San José, Costa Rica",
                "tipo_cedula": "personal",
                "numero_cedula": "3007001010"
            }
        }