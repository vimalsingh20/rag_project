from sklearn.metrics.pairwise import cosine_similarity
from utils.logger import get_logger 
from utils.exception import CustomException
import sys 

logger = get_logger(__name__)

def retrive_chunks (query_embedding,records,top_k=3,threshold =0.5):
    try:
        
        embeddings = [
            record['embedding']
            for record in records
        ]
        similarities = cosine_similarity(
            [query_embedding],
            embeddings
        )[0]
        
        top_indices = similarities .argsort()[-top_k:][::-1]
        
        retrieved_results = []
        for i in top_indices: 
            score = similarities[i]
            
            if score >= threshold:
                result = { 
                          "chunk":records[i]['chunk'],
                          "score":float(score),
                          "document":records[i]['document'],
                          'chunk_id':records[i]['chunk_id']
                        }
                
                retrieved_results.append(result)
                
                             
        logger.info("Structured retrival completed sucessfully")
        
        return retrieved_results
    
    except Exception as e : 
        logger.error ("error during retrival")
        
        raise CustomException (e,sys)