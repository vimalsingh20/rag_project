import json 
import os 
from datetime import datetime, timedelta
CACHE_DIR = "embedding_cache"

def save_embedding_cache(
    file_hash,records):
    
    cache_path = f"{CACHE_DIR} /{file_hash}.json"
    with open (cache_path,"w") as file:
        json.dump (records,file,indent=4)
        
    print(f"\nEmbedding cache saved: {file_hash}")    
    
    
def cleanup_old_cache(days=30):
    now = datetime.now()
    for filename in os.listdir(CACHE_DIR):
        file_path = f"{CACHE_DIR}/{filename}"
        created_time = datetime.fromtimestamp(
            os.path.getctime(file_path)
        )
        expiry_date = created_time + timedelta(days=days)
        if now > expiry_date:
            os.remove(file_path)
            print(f"\nDeleted old cache: {filename}")    