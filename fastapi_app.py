from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from transformers import pipeline
import os

app = FastAPI(title="FlexAI Local Machine Learning Interface")

import torch

print("Loading local AI model into memory. Please wait...")
try:
    chatbot_pipeline = pipeline(
        "text-generation", 
        model="Qwen/Qwen2.5-0.5B-Instruct", 
        device="cpu",
        torch_dtype=torch.float32  # Use float32 for CPU compatibility and speed
    )
    print("Model loaded successfully!")
except Exception as e:
    print("Error loading local model:", e)
    chatbot_pipeline = None

class ChatRequest(BaseModel):
    message: str
    system_prompt: str = "You are FlexAI Gym Trainer, a professional virtual fitness coach. Keep answers SHORT (3-5 lines). Use simple English."

class ChatResponse(BaseModel):
    response: str

class NotificationRequest(BaseModel):
    user_name: str
    streak: int
    calories_today: int
    total_workouts: int
    notification_type: str # MORNING, DIET, EVENING, NIGHT, EVENT
    language: str = "English"

class NotificationResponse(BaseModel):
    title: str
    message: str

@app.post("/chat/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if chatbot_pipeline is None:
        raise HTTPException(status_code=500, detail="Local AI Model failed to load.")
    
    messages = [
        {"role": "system", "content": request.system_prompt},
        {"role": "user", "content": request.message}
    ]
    
    try:
        outputs = chatbot_pipeline(
            messages, 
            max_new_tokens=500, # Increased output length to allow detailed explanations
            do_sample=False,   # Greedy decoding is much faster than sampling
            temperature=None,
            top_p=None
        )
        ai_text = outputs[0]['generated_text'][-1]['content']
        return ChatResponse(response=ai_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation Error: {str(e)}")

@app.get("/chat/", response_class=HTMLResponse)
async def get_knowledge_base():
    """Display the Fitness Knowledge Base for the guide to see."""
    kb_path = os.path.join(os.path.dirname(__file__), "api", "fitness_knowledge_base.txt")
    if not os.path.exists(kb_path):
        return "<h1>Knowledge Base Not Found</h1>"
    
    with open(kb_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Return as formatted HTML for the guide
    html_content = f"""
    <html>
        <head>
            <title>FlexAI Knowledge Base</title>
            <style>
                body {{ font-family: sans-serif; padding: 40px; line-height: 1.6; background-color: #f4f4f9; }}
                .container {{ max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                pre {{ background: #fdf6e3; padding: 15px; border-radius: 4px; overflow-x: auto; white-space: pre-wrap; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>FlexAI Fitness Knowledge Base</h1>
                <p>This is the <b>"Matter"</b> used by the AI to provide expert fitness advice.</p>
                <pre>{content}</pre>
                <hr>
                <p><small>Generated locally by FlexAI Backend</small></p>
            </div>
        </body>
    </html>
    """
    return html_content

@app.post("/generate_notification/", response_model=NotificationResponse)
async def generate_notification(request: NotificationRequest):
    if chatbot_pipeline is None:
        return NotificationResponse(title="FlexAI Reminder", message="Keep up your great work today!")
    
    prompt = f"""
    Generate a short, engaging fitness notification for {request.user_name}.
    Context:
    - Type: {request.notification_type}
    - Current Streak: {request.streak} days
    - Calories today: {request.calories_today}
    - Total workouts: {request.total_workouts}
    - Language: {request.language}

    Rules:
    - Title should be catchy (max 5 words).
    - Message should be motivating (max 15 words).
    - Response format: Title | Message
    """

    try:
        messages = [{"role": "user", "content": prompt}]
        outputs = chatbot_pipeline(messages, max_new_tokens=100, do_sample=False)
        result = outputs[0]['generated_text'][-1]['content'].strip()
        
        if "|" in result:
            parts = result.split("|")
            return NotificationResponse(title=parts[0].strip(), message=parts[1].strip())
        else:
            return NotificationResponse(title="Fitness Update", message=result)
            
    except Exception as e:
        return NotificationResponse(title="FlexAI Reminder", message="Keep pushing towards your goals!")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
