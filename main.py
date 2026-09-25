import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

# Enable CORS so your Hugging Face frontend can make fetch calls to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# Microsoft Phi-3 Medium Serverless Inference Endpoints API Destination
HF_API_URL = "https://huggingface.co"
HF_TOKEN = os.getenv("HF_TOKEN")

@app.post("/webhook/huggingface")
async def chat_with_phi3(payload: ChatRequest):
    if not HF_TOKEN:
        raise HTTPException(
            status_code=500, 
            detail="Server Config Error: HF_TOKEN missing from environment variables."
        )
    
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    hf_payload = {
        "inputs": f"<|user|>\n{payload.message}<|end|>\n<|assistant|>",
        "parameters": {
            "max_new_tokens": 512,
            "return_full_text": False
        }
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=hf_payload)
        
        # Check if the Hugging Face model container is cold and booting up
        if response.status_code == 503:
            return {"reply": "Tanishqa AI is currently warming up its engines. Please try sending your message again in a few seconds!"}
            
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        result = response.json()
        
        # Clean string extraction out of standard multi-element list frames
        if isinstance(result, list) and len(result) > 0:
            ai_text = result[0].get("generated_text", "No response content generated.")
        else:
            ai_text = result.get("generated_text", "Format issue from Inference gateway.")

        return {"reply": ai_text.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
