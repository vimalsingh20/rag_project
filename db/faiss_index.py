import faiss
import numpy as np
from pathlib import Path
import shutil

from utils.logger import get_logger
from config.settings import (
    FAISS_DIMENSION,
    VECTOR_INDEX_FOLDER)
logger = get_logger(__name__)

class FaissIndex:
    def __init__(
        self,
        document_id: int,
        dimension: int = FAISS_DIMENSION):

        self.document_id = document_id
        self.dimension = dimension

        self.index = None

        self.index_dir = (
            Path(VECTOR_INDEX_FOLDER)
            / str(document_id))

        self.index_path = (
            self.index_dir
            / "faiss.index")

    def load_or_create_index(self):

        self.index_dir.mkdir(
            parents=True,
            exist_ok=True)

        if self.index_path.exists():

            self.index = faiss.read_index(
                str(self.index_path))
            logger.info(
                f"FAISS index loaded for document {self.document_id}")
        else:

            self.index = faiss.IndexFlatL2(
                self.dimension)

            logger.info(
                f"New FAISS index created for document {self.document_id}")
    def save_index(self):
        if self.index is None:
            raise ValueError(
                "No FAISS index to save.")
        faiss.write_index(
            self.index,
            str(self.index_path))
        logger.info(
            f"FAISS index saved for document {self.document_id}")
    def add_embeddings(
        self,
        embeddings):
        if self.index is None:
            raise ValueError(
                "FAISS index not loaded.")
        if len(embeddings) == 0:
            return
        embedding_array = np.array(
            embeddings,
            dtype=np.float32)
        self.index.add(
            embedding_array)
        self.save_index()
        logger.info(
            f"{len(embeddings)} embeddings added.")
    def search(
        self, query_embedding,top_k=3):

        if self.index is None:
            raise ValueError(
                "FAISS index not loaded."
            )

        if self.index.ntotal == 0:
            return [], []

        query_array = np.array(
            [query_embedding],
            dtype=np.float32
        )

        distances, indices = self.index.search(
            query_array,
            top_k
        )

        return distances, indices

    def delete_index(self):

        if self.index_dir.exists():

            shutil.rmtree(
                self.index_dir
            )

            logger.info(
                f"FAISS index deleted for document {self.document_id}"
            )

        self.index = None

    def retrieve(
        self,
        query_embedding,
        chunks,
        top_k=3
    ):

        if self.index is None:
            raise ValueError(
                "FAISS index not loaded."
            )

        distances, indices = self.search(
            query_embedding,
            top_k
        )

        results = []

        for idx, distance in zip(
            indices[0],
            distances[0]
        ):

            if idx == -1:
                continue

            if idx >= len(chunks):
                continue
            chunk = chunks[idx].copy()
            chunk["distance"] = float(distance)

            results.append(chunk)
        return results