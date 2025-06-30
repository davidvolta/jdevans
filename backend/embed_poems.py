from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
client = OpenAI()

with open("poems.json", "r") as f:
    poems = json.load(f)

poems = [{**poem, "id": i} if "id" not in poem else poem for i, poem in enumerate(poems)]

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

for poem in tqdm(poems):
    full_text = f"{poem['title']}\n{poem['content']}\n{poem['signature']}"
    poem["embedding"] = get_embedding(full_text)

with open("poems_with_embeddings.json", "w") as f:
    json.dump(poems, f)
