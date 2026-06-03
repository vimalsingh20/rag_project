from utils.logger import get_logger 
from utils.exception import CustomException
import sys
import json 
import os
from datetime import datetime 

logger = get_logger(__name__)
METADATA_PATH = "saved_index/records.json"

class VectorStore:
    def __init__(self):
        if os.path.exists(METADATA_PATH):
            with open(METADATA_PATH, "r") as file:
                self.records = json.load(file)
            logger.info("Metadata loaded successfully.")

        else:
            self.records = []
            logger.info("New metadata store created.")

    def add_embedding(
    self,
    chunks,
    embeddings,
    document_name,
    file_hash
):
        try:
            for idx, (chunk, embedding) in enumerate(
                zip(chunks, embeddings)
            ):
                record = {
                    "chunk": chunk,
                    "embedding": embedding.tolist(),
                    "document": document_name,
                    "chunk_id": idx,
                    "file_hash":file_hash,
                    "upload_time": datetime.now().isoformat()
                }
                self.records.append(record)
            with open(METADATA_PATH, "w") as file:
                json.dump(
                    self.records,file,indent=4)

            logger.info("Structured records stored successfully.")

        except Exception as e:
            logger.error(
                "Error storing structured records" )
            raise CustomException(e, sys)

    def get_records(self):
        return self.records
    
    def save_records(self):

        with open(METADATA_PATH,"w") as file:

            json.dump(self.records,file,indent=4)

        logger.info(
        "Metadata saved successfully.")