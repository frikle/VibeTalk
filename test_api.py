import aiohttp
import asyncio
import json

API_KEY = "AIzaSyD-ZgxbLkzxosjTmegfzfoAg8IzuAy6bC0"
API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
MODEL_NAME = "gemini-3.8-flash"

async def test():
    url = f"{API_BASE_URL}/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": "Say hello"}]}],
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": 100}
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            print(f"Status: {resp.status}")
            data = await resp.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))

asyncio.run(test())
