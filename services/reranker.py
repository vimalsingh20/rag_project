def rerank_chunks(question,retrived_chunks):
    question_words = set(question.lower().split())
    scored_chunks=[]
    for chunk in retrived_chunks:
        chunks_text = chunk['chunk'].lower()
        chunk_words = set(chunks_text.split())
        
        score = len(question_words.intersection(chunk_words))
        scored_chunks.append((score, chunk))
        scored_chunks.sort(reverse= True,key=lambda x:x[0])
        
        rereanked_chunks = [chunk
                            for score,chunk in scored_chunks]
        
    return rereanked_chunks        