from utils. logger import get_logger
from utils.exception import CustomException
import sys 

from config.settings import (
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

logger = get_logger(__name__)

def split_text(
    text: str,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP
):
    
    try:
        words = text.split()
        chunks = []
        
        step = chunk_size - overlap
        
        for i in range (0,len(words),step):
            chunk_words  = words [i:i +chunk_size]
            chunk = " ".join(chunk_words)
            chunks .append(chunk)
            
        logger.info(f"Text split into{len(chunks)} chunks")
        return chunks 
    
    except Exception as e : 
        logger.error("Errorin chunking")
        
        raise CustomException (e,sys)    