def keyword_retrieve (question,records,top_k=3):
    question_words = set(question.lower().split())
    
    scored_chunks =[]
    for record in records :
        chunk_text = record['chunk'].lower()
        
        chunk_words = set(chunk_text.split())
        
        overlap_score = len(question_words.intersection(chunk_words))
        
        scored_chunks.append((overlap_score,record))
        
        scored_chunks.sort(
            reverse=True,
            key=lambda x:x[0]
        )
        
        top_chunks = [record
                      for score,record in scored_chunks[:top_k]
                      if score >0 ] 
        
        return top_chunks
        