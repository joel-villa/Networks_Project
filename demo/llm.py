import asyncio
from ollama import AsyncClient

MODEL = "qwen2.5:3b"
IP = "100.84.137.98"
HOST = f"http://{IP}:11434"
INIT_PROMPT = {'role': 'system', 'content': 'Restrict responses to 150 character max, be consise but not short'}

async def get_response(prompt):
  client = AsyncClient(host=HOST)

  messages = [
    INIT_PROMPT,
    {'role': 'user', 'content': prompt}
  ]
  
  response = await client.chat(
    model = MODEL,
    messages = messages,
    stream = False,
    options = {
      'num_predict': 45,
      'temperature': .2
    }
  )
  return response['message']['content']

async def main():
  PROMPT = 'Tell me about New Mexico'
  reply = await get_response(PROMPT)
  print(f"Response: {reply}")
  
if __name__ ==  "__main__":
  asyncio.run(main())
