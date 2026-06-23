import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

res = client.chat.completions.create(
    model="llama-3.1-8b-instant",   # ✅ FIXED MODEL
    messages=[
        {"role": "user", "content": "Hello"}
    ]
)

print(res.choices[0].message.content)