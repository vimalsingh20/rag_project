from sentence_transformers import SentenceTransformer 
from utils.logger import get_logger 
from utils.exception import CustomException 
import sys 
from config.settings import EMBEDDING_MODEL


logger = get_logger(__name__)
model = SentenceTransformer(EMBEDDING_MODEL)

def get_embedding(chunks: list):
    try:
        if not chunks :
            logger.warning ("Empty chunk list received")
            return []
        embedding = model.encode (chunks)
        
        logger.info(f"Created embedding for {len(chunks)} chunks")
        
        return embedding
    
    except Exception as e : 
        logger.error ("error while genrating embedding")
        
        raise CustomException(e,sys)