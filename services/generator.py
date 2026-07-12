import os 
import google.generativeai as genai
from dotenv import load_dotenv
from utils.logger import get_logger
from utils.exception import CustomException

from prompts.rag_prompt import RAG_PROMPT

import sys 
load_dotenv()

genai.configure ( 
                 api_key = os.getenv("GOOGLE_API_KEY"))

logger  = get_logger(__name__)
model = genai.GenerativeModel(
    "models/gemini-2.5-flash"
)

def generate_answer(question,retrieved_chunks):
    try:
        if not retrieved_chunks:
            return "I could not find the answer in the uploaded document."
        context = "\n\n".join(

    [
        f"[Context {idx+1}]\n{result['chunk'][:1000]}"

        for idx, result in enumerate(retrieved_chunks[:3])
    ]
)
        prompt = RAG_PROMPT.format(
    context=context,
    question=question
)  
        logger.info(f"Context Length: {len(context)}") 
        response = model.generate_content(prompt,request_options={"timeout":60})
       
        logger.info("answer generated sucessfully")
        return response.text
    
    except Exception as e:
        logger.error('error generating answer')
        
        raise CustomException (e,sys)
        
        