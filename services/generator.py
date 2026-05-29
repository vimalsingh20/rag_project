import os 
import google.generativeai as genai
from dotenv import load_dotenv
from utils.logger import get_logger
from utils.exception import CustomException

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
        context = "\n\n".join(

    [
        f"[Context {idx+1}]\n{result['chunk'][:1000]}"

        for idx, result in enumerate(retrieved_chunks[:3])
    ]
)
        prompt = f"""
You are a helpful AI assistant.
Answer the question using ONLY the provided context.
If the exact answer is not available,
try to provide the closest relevant information
from the context.
Only say:
"I could not find the answer in the provided document."
if absolutely no relevant information exists.

Context:

{context}

Question:
{question}

Answer:
"""     
        print(f"Context Length: {len(context)}") 
        response = model.generate_content(prompt,request_options={"timeout":60})
       
        logger.info("answer generated sucessfully")
        return response.text
    
    except Exception as e:
        logger.error('error generating answer')
        
        raise CustomException (e,sys)
        
        