import openai
import os

# Make sure your environment variable is set correctly
openai.api_key = os.getenv("OPENAI_API_KEY")

# New style import (no longer openai.ChatCompletion.create)
client = openai.OpenAI()

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Hello, how are you?"},
        ]
    )
    print("✅ Success:", response.choices[0].message.content)
except Exception as e:
    print("❌ Error:", e)
