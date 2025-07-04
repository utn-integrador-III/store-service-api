from pymongo import MongoClient
from decouple import config
import logging
from bson.objectid import ObjectId
from fastapi import HTTPException, status
from typing import List, Dict

client = MongoClient(config("MONGO_URL"))
db = client[config("MONGO_DB")]

def serialize_document(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

class Connection:
    def __init__(self, collection_name: str):
        self.collection = db[collection_name]

    def get_all_data(self) -> List[Dict]:
        try:
            cursor = self.collection.find({})
            return [serialize_document(doc) for doc in cursor]
        except Exception as e:
            logging.error(f"Error en get_all_data: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al consultar los datos.")

    def find_one(self, query: Dict) -> Dict:
        try:
            result = self.collection.find_one(query)
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado.")
            return serialize_document(result)
        except HTTPException as he:
            raise he
        except Exception as e:
            logging.error(f"Error en find_one: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al buscar el documento.")

    def get_by_id(self, id: str) -> Dict:
        try:
            result = self.collection.find_one({"_id": ObjectId(id)})
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Documento con id '{id}' no encontrado.")
            return serialize_document(result)
        except HTTPException as he:
            raise he
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de ID inválido.")

    def create_data(self, data: Dict) -> Dict:
        try:
            result = self.collection.insert_one(data)
            new_doc = self.collection.find_one({"_id": result.inserted_id})
            return serialize_document(new_doc)
        except Exception as e:
            logging.error(f"Error en create_data: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el documento.")

    def update_data(self, id: str, new_data: Dict) -> bool:
        self.get_by_id(id)
        try:
            result = self.collection.update_one({"_id": ObjectId(id)}, {"$set": new_data})
            return result.modified_count > 0
        except Exception as e:
            logging.error(f"Error en update_data: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el documento.")

    def delete_data(self, id: str) -> bool:
        self.get_by_id(id)
        try:
            result = self.collection.delete_one({"_id": ObjectId(id)})
            return result.deleted_count > 0
        except Exception as e:
            logging.error(f"Error en delete_data: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el documento.")