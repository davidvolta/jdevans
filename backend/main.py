from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
from typing import List, Optional
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="J.D. Evans Poem Generator API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
        "https://jdevans-app.onrender.com",
        "https://www.jdevanspoems.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("poems_with_embeddings.json", "r") as f:
    SAMPLE_POEMS = json.load(f)

# Extract all embedding vectors into a matrix for cosine similarity
EMBEDDING_VECTORS = np.array([poem["embedding"] for poem in SAMPLE_POEMS])

client = OpenAI()

class GenerateRequest(BaseModel):
    prompt: str

class SimilarPoem(BaseModel):
    id: int
    title: str
    content: str
    signature: str
    score: float

class GenerateResponse(BaseModel):
    title: str
    body: str
    signature: str
    similar_poems: List[SimilarPoem]
    illustration_prompt: Optional[str] = None
    illustration_url: Optional[str] = None
    poem_id: Optional[str] = None

# In-memory cache of illustrations keyed by poem ID
ILLUSTRATION_CACHE = {}

def find_similar_poems(prompt: str, top_k: int = 3) -> List[dict]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=prompt
    )
    prompt_vector = np.array(response.data[0].embedding).reshape(1, -1)
    similarities = cosine_similarity(prompt_vector, EMBEDDING_VECTORS).flatten()
    top_indices = similarities.argsort()[-top_k:][::-1]
    similar_poems = []
    for idx in top_indices:
        poem = SAMPLE_POEMS[int(idx)]
        similar_poems.append({
            "id": poem["id"],
            "title": poem["title"],
            "content": poem["content"],
            "signature": poem["signature"],
            "score": float(similarities[idx])
        })
    return similar_poems

def generate_poem_with_openai(prompt: str, similar_poems: List[str]) -> dict:
    style_modifier = ""

    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": (
                "You are J.D. Evans, a clever and heartfelt South Jersey newspaper columnist and poet. "
                "Your poems are short, humorous, occasionally satirical or poignant reflections on everyday American life that often use unexpected metaphors. "
                "Your tone is conversational, self-deprecating, observational, and moral, with a wry or bittersweet undercurrent. "
                "You frequently write in formal rhyme and meter."
                "You often adopt parodic or whimsical variations of established forms of poetry. "
                "You analyze and reflect on your rhythm before writing. "
                "Your poems ALWAYS end with a humorous biographical signature related to the poem in the form '(J.D. Evans, a pseudonym, is [statement related to poem] … occasionally)'. "
                "Always sign your poems with a version of this line. "
                "Generate poems in this style—playful, reflective, and rhythmically engaging—grounded in the ordinary absurdities of American life."
                "Here is a short biography of your life to influence details in your poems: JD Evans was born in South Jersey and came of age in a postwar American household shaped by Catholic school discipline, modest means, and a culture of stoicism. His early life was marked by structured learning environments, most notably described in his poem about Sister Francis, a strict nun who disciplined students with ruler-smacks and a rigid educational philosophy. Despite the severity of his schooling, JD Evans retained a warm humor about his upbringing and would carry that sensibility into his later writing, blending affection with gentle satire. His poetic voice suggests early literary inclinations, an ear for rhythm and rhyme, and a skepticism of authority that deepened over time. As a young father, JD Evans found great joy in parenting, often elevating the mundane into the poetic. His poems speak lovingly of fatherhood—of paddling the Oswego River with his sons, fixing tangled Christmas lights, and watching his boys grow from toddlers to men. His humor often reflected frustrations with the everyday—stock market gibberish, jogging excuses, barbecue mishaps—but behind each quip was a man grounded in familial love and moral reflection. Professionally, he worked in public relations and journalism, perhaps in local New Jersey media, and it's clear he kept a close watch on current events, politics, and popular culture, responding to them with wit and occasional satire. In later years, JD Evans's writing turned more reflective, acknowledging the passing of time, the erosion of shared experiences, and the inexorable ticking of life's clock. He retained his sharp eye for absurdity but often aimed it inward, wrestling with questions of aging, meaning, and legacy. A passionate observer of local life, he remained deeply connected to South Jersey, chronicling its quirks, politics, and people with both fondness and critique. Until the end, JD Evans continued to write with the same mix of playfulness and poignancy, leaving behind a body of work that documents not just a region or an era, but a father's life—observed honestly, humorously, and occasionally."
            )
        },
        {
            "role": "user",
            "content": (
                style_modifier +
                f"Write a poem inspired by the following theme: {prompt}.\n\n"
                f"Here are a few past poems for style and rhythm inspiration:\n\n" +
                "\n\n---\n\n".join(similar_poems) +
                "\n\nFirst, analyze the rhythm of each past poem by writing the perceived stress pattern of each line using 'U' for unstressed and '/' for stressed syllables. "
                "Choose one poem you have the most confidence in and use its metrical fingerprint (U and /) to guide the rhythm of your new poem. When in doubt use anapestic tetrameter."
                "Then, write a new poem that matches or mirrors the rhythm and rhyme pattern.\n\n"
                "Return the result as a JSON object with the following fields:\n"
                "{\n"
                '  "title": "The title of the poem",\n'
                '  "body": "The poem body, with line breaks as \\n",\n'
                '  "signature": "The signature line, e.g. (J.D. Evans, ...)"\n'
                "}\n"
                "Do not include any text outside the JSON object."
            )
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    content = response.choices[0].message.content
    if content is None:
        raise HTTPException(status_code=500, detail="Failed to generate poem")
    content = content.strip()
    poem_json = json.loads(content)
    return poem_json

def extract_visual_prompt(poem_body: str) -> str:
    system_msg = "You are a visual prompt generator. Given a poem, extract a scene as if describing it to an illustrator."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": poem_body}
        ]
    )
    content = response.choices[0].message.content
    if content is None:
        raise HTTPException(status_code=500, detail="Failed to generate visual prompt")
    return content.strip()

def combine_with_style(scene: str) -> str:
    style = "A black-and-white ink cartoon in the style of mid-to-late 20th century American comics and editorial strips, reminiscent of op-eds from the 1980s. The artwork features bold, expressive line work, with thick, uneven outlines with almost no crosshatching or stippling. Minimal shading for texture and contrast. The humor is either slapstick or charming, never both. Scenes are personality-driven, and full of comic tension. No color. Just stark black ink on white."
    return f"{style} {scene}"

def generate_illustration(full_prompt: str) -> str:
    response = client.images.generate(
        model="dall-e-3",
        prompt=full_prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )
    if not response.data or len(response.data) == 0:
        raise HTTPException(status_code=500, detail="Failed to generate illustration")
    url = response.data[0].url
    if url is None:
        raise HTTPException(status_code=500, detail="Failed to generate illustration")
    return url

def save_user_poem(poem_data: dict, prompt: str):
    # Get the next ID by finding the highest existing ID and adding 1
    try:
        with open("poems.json", "r") as f:
            poems = json.load(f)
        next_id = max(poem["id"] for poem in poems) + 1 if poems else 1
    except FileNotFoundError:
        poems = []
        next_id = 1

    user_poem = {
        "id": next_id,
        "title": poem_data["title"],
        "content": poem_data["body"],  # Note: existing poems use "content" not "body"
        "signature": poem_data["signature"],
        "prompt": prompt
    }

    poems.append(user_poem)

    with open("poems.json", "w") as f:
        json.dump(poems, f, indent=2)

@app.post("/generate", response_model=GenerateResponse)
async def generate_poem(request: GenerateRequest, background_tasks: BackgroundTasks):
    similar_poems = find_similar_poems(request.prompt)
    similar_poem_texts = [
        f"{poem['title']}\n{poem['content']}\n{poem['signature']}"
        for poem in similar_poems
    ]
    poem_data = generate_poem_with_openai(request.prompt, similar_poem_texts)
    poem_id = str(uuid.uuid4())

    def background_image_generation(poem_body, pid):
        try:
            visual_prompt = extract_visual_prompt(poem_body)
            full_prompt = combine_with_style(visual_prompt)
            illustration_url = generate_illustration(full_prompt)
            ILLUSTRATION_CACHE[pid] = {
                "illustration_prompt": visual_prompt,
                "illustration_url": illustration_url
            }
        except Exception as e:
            print(f"[Background Illustration Error]: {e}")

    background_tasks.add_task(background_image_generation, poem_data["body"], poem_id)
    poem_data["similar_poems"] = similar_poems
    poem_data["poem_id"] = poem_id
    
    # Save the user poem to poems.json
    save_user_poem(poem_data, request.prompt)
    
    return GenerateResponse(**poem_data)

@app.get("/illustration")
async def get_illustration(poem_id: str):
    if poem_id not in ILLUSTRATION_CACHE:
        return {"status": "pending"}
    return {"status": "ready", **ILLUSTRATION_CACHE[poem_id]}

@app.get("/poems")
async def get_poems():
    """Get all archive poems"""
    try:
        with open("poems.json", "r") as f:
            poems = json.load(f)
        # Return poems in reverse order (newest first)
        poems_reversed = list(reversed(poems))
        return {"poems": poems_reversed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load poems: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
