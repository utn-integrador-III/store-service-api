# models/enterprise.py
from pydantic import BaseModel

class Enterprise(BaseModel):
    id_empresa: str
    nombre_empresa: str
    categoria: str
    informacion_empresa: str
    horario: str
    telefono: str
    correo_electronico: str
    direccion: str
    tipo_cedula: str
    numero_cedula: str