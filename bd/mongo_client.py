# bd/mongo_client.py (ESTE ES EL CÓDIGO QUE DEBES TENER)

from pymongo import MongoClient
from decouple import config
import logging
from bson.objectid import ObjectId
from fastapi import HTTPException, status
from typing import List, Dict, Optional # Asegúrate de que Optional esté importado
from bson.errors import InvalidId

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# --- MongoDB Connection ---
try:
    mongo_url = config("MONGO_URL").strip()
    mongo_db_name = config("MONGO_DB").strip()
    client = MongoClient(mongo_url)
    db = client[mongo_db_name]
    client.admin.command('ping')
    logging.info("MongoDB connection successful!")
except Exception as e:
    logging.critical(f"Could not connect to MongoDB: {e}")
    raise Exception(f"Failed to connect to database: {e}")

def get_database():
    return db

def serialize_document(doc: Optional[Dict]) -> Optional[Dict]:
    if doc:
        serialized_doc = doc.copy()
        if "_id" in serialized_doc:
            serialized_doc["_id"] = str(serialized_doc["_id"])
        return serialized_doc
    return None

class Connection:
    def __init__(self, collection_name: str):
        self.collection = db[collection_name]
        logging.info(f"Connection established for collection: {collection_name}")

    def get_all_data(self) -> List[Dict]:
        try:
            cursor = self.collection.find({})
            return [serialize_document(doc) for doc in cursor if doc is not None]
        except Exception as e:
            logging.error(f"Error in get_all_data for collection {self.collection.name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al consultar los datos."
            )

    # --- MÉTODO find_one MODIFICADO ---
    def find_one(self, query: Dict) -> Optional[Dict]: # Ahora retorna Optional[Dict]
        """
        Busca un solo documento que coincida con la consulta dada.
        Retorna el documento serializado si se encuentra, de lo contrario retorna None.
        Lanza HTTPException 500 para errores de base de datos.
        """
        try:
            result = self.collection.find_one(query)
            # YA NO LANZAMOS EL 404 AQUÍ. El controlador lo manejará.
            return serialize_document(result)
        except Exception as e:
            logging.error(f"Error in find_one for collection {self.collection.name} with query {query}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al buscar el documento."
            )

    # El método get_by_id SÍ debe lanzar un 404 si no encuentra el ID,
    # porque ese es su propósito: obtener un documento específico por su ID.
    def get_by_id(self, doc_id: str) -> Dict:
        cleaned_id = doc_id.strip()
        try:
            obj_id = ObjectId(cleaned_id)
        except InvalidId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El formato del ID '{cleaned_id}' no es válido."
            )
        try:
            result = self.collection.find_one({"_id": obj_id})
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No se encontró un documento con el id '{cleaned_id}'."
                )
            return serialize_document(result)
        except HTTPException as he:
            raise he
        except Exception as e:
            logging.error(f"Database error in get_by_id for collection {self.collection.name} with ID {cleaned_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ocurrió un error inesperado al consultar la base de datos."
            )

    def create_data(self, data: Dict) -> Dict:
        try:
            result = self.collection.insert_one(data)
            new_doc = self.collection.find_one({"_id": result.inserted_id})
            if not new_doc:
                logging.error(f"Failed to retrieve newly created document with ID: {result.inserted_id}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al recuperar el documento recién creado."
                )
            return serialize_document(new_doc)
        except Exception as e:
            logging.error(f"Error in create_data for collection {self.collection.name} with data {data}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al crear el documento."
            )


    def find_many(self, query: Dict) -> List[Dict]:
        try:
            cursor = self.collection.find(query)
            results = [serialize_document(doc) for doc in cursor if doc is not None]
            return results
        except Exception as e:
            logging.error(f"Error in find_many for collection {self.collection.name} with query {query}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al buscar los documentos."
            )