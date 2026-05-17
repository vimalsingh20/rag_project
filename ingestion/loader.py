import fitz 
from utils.logger import get_logger
from utils.exception import CustomException
import sys 

logger = get_logger(__name__)

def load_pdf(file_path: str) -> str:
    text = ""
    
    try:
        doc = fitz.open(file_path)
        
        for page in doc : 
            text+= page.get_text()
            
        logger.info ("PDF loaded sucessfully")
        
        return text 
    
    except Exception as e : 
        logger.error ("Error loading PDF")
        raise CustomException (e,sys)    