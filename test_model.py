import os
import sys

try:
    from transformers import pipeline
except ImportError:
    print("Transformers not yet installed. Waiting.")
    sys.exit(1)

print("Starting model download. Please wait...")
chatbot_pipeline = pipeline("text-generation", model="Qwen/Qwen2.5-0.5B-Instruct", device="cpu")

system_prompt = "You are FlexAI Gym Trainer, a professional virtual fitness coach. Keep answers SHORT (3–5 lines). Use simple English."
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "How do I do pushups?"}
]

print("Model loaded. Testing generation:")
outputs = chatbot_pipeline(messages, max_new_tokens=50)
print(outputs[0]['generated_text'][-1]['content'])
print("SUCCESS!")
