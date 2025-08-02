
from bson import ObjectId
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from typing import Any

class PyObjectId(ObjectId):
    """
    Clase personalizada para manejar los ObjectId de MongoDB
    compatible con Pydantic V2 y FastAPI.
    """
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        object_id_schema = core_schema.with_info_plain_validator_function(cls.validate)
        
        return core_schema.json_or_python_schema(
            json_schema=object_id_schema,
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                object_id_schema
            ]),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v: Any, info: core_schema.ValidationInfo):
        """
        Valida que el valor de entrada sea un ObjectId válido.
        """
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetCoreSchemaHandler
    ):
        return {"type": "string"}