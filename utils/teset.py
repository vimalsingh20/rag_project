from utils.logger import get_logger
from utils.exception import CustomException

import sys 

logger = get_logger(__name__)

try:
    a = 1/0
    
except Exception as e : 
    logger.error ("something went wrong")
    
    raise CustomException(e,sys)    