from rank_bm25 import BM25Okapi

def bm25_retrieve(query,records,top_k=3):
    if not records:
        return[]
    
    corpus =[record['chunk'].split()  
    for record in records]
    
    bm25 =BM25Okapi(corpus)
    tokenized_query =query.split()
    scores =bm25.get_scores(tokenized_query)
    
    ranked_results = sorted(zip(records,scores),
                            key =lambda x:x[1],
                            reverse = True)
    return [result[0] for result in ranked_results[:top_k]]


    