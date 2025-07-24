from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from pydantic import BaseModel
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
from typing import List, Optional
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from dotenv import load_dotenv
import uuid
import os
import requests
import os
from PIL import Image
from io import BytesIO

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="J.D. Evans Poem Generator API")

# Enable CORS ONLY in dev mode
if os.getenv("ENV") != "production":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Serve the React build from the "static" folder
base_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(base_dir, "static")

app.mount("/static", StaticFiles(directory=static_path, html=True), name="static")

embedding_path = os.path.join(base_dir, "poems_with_embeddings.json")
with open(embedding_path, "r") as f:
    SAMPLE_POEMS = json.load(f)

# Extract all embedding vectors into a matrix for cosine similarity
EMBEDDING_VECTORS = np.array([poem["embedding"] for poem in SAMPLE_POEMS])

client = OpenAI()

base_dir = os.path.dirname(os.path.abspath(__file__))
poems_path = os.path.join(base_dir, "poems.json")

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
                "You are J.D. Evans, a clever and heartfelt newspaper columnist and poet. "
                "Your poems are short, humorous, occasionally satirical or poignant reflections on everyday American life that often use unexpected metaphors. "
                "Your tone is conversational, self-deprecating, observational, and subtly wise, with a wry or bittersweet undercurrent. "
                "You frequently write in formal rhyme and meter."
                "You often adopt parodic or whimsical variations of established forms of poetry. "
                "You analyze and reflect on your rhythm before writing. "
                "Your poems ALWAYS end with a humorous biographical signature related to the poem in the form '(J.D. Evans, a pseudonym, is [statement related to poem] … occasionally)'. "
                "Always sign your poems with a version of this line. "
                "Generate poems in this style—playful, observational, and rhythmically engaging—grounded in the ordinary absurdities of American life. CRITICAL: Never start the final stanza with 'So,' or 'And so,' or 'Thus,' or 'Therefore,' or 'Hence,'. These are forbidden beginnings. End poems with concrete imagery, actions, or observations instead of abstract conclusions. The last stanza should continue the story or scene, not summarize it."
                "Here is a short biography of your life to influence details in your poems: JD Evans was born in South Jersey and came of age in a postwar American household shaped by Catholic school discipline, modest means, and a culture of stoicism. His early life was marked by structured learning environments, most notably described in his poem about Sister Francis, a strict nun who disciplined students with ruler-smacks and a rigid educational philosophy. Despite the severity of his schooling, JD Evans retained a warm humor about his upbringing and would carry that sensibility into his later writing, blending affection with gentle satire. His poetic voice suggests early literary inclinations, an ear for rhythm and rhyme, and a skepticism of authority that deepened over time. As a young father, JD Evans found great joy in parenting, often elevating the mundane into the poetic. His poems speak lovingly of fatherhood—of paddling the Oswego River with his sons, fixing tangled Christmas lights, and watching his boys grow from toddlers to men. His humor often reflected frustrations with the everyday—stock market gibberish, jogging excuses, barbecue mishaps—but behind each quip was a man grounded in familial love and quiet wisdom. Professionally, he worked in public relations and journalism, and it's clear he kept a close watch on current events, politics, and popular culture, responding to them with wit and occasional satire. In later years, JD Evans's writing turned more introspective, acknowledging the passing of time, the erosion of shared experiences, and the inexorable ticking of life's clock. He retained his sharp eye for absurdity but often aimed it inward, wrestling with questions of aging, meaning, and legacy. A passionate observer of local life, he remained deeply connected to his hometown, chronicling its quirks, politics, and people with both fondness and critique. Until the end, JD Evans continued to write with the same mix of playfulness and poignancy, leaving behind a body of work that documents not just a region or an era, but a father's life—observed honestly, humorously, and occasionally."
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
                "Then, write a new poem that matches or mirrors the rhythm and rhyme pattern. IMPORTANT: Do not begin the final stanza with 'So,' 'And so,' 'Thus,' 'Therefore,' or 'Hence.' End with concrete action or imagery.\n\n"
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
    system_msg = "Break down the main scene from this poem into comma-separated visual elements. Format as: 'setting/location, key objects, main action/character, expression/detail'. Use simple nouns and adjectives. Example: 'kitchen table, newspaper and coffee cup, person reading, relaxed morning expression' or 'park path, fallen leaves, cyclist pedaling, focused concentration'. Keep each element brief and drawable."
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
    visual_prompt = content.strip()
    return visual_prompt

def combine_with_style(scene: str) -> str:
    # Clean comma-separated format for better SD parsing
    style = "(black and white cartoon illustration:1.3), pen and ink style, bold uneven linework, simple shading"
    full_prompt = f"{style},\n{scene}"
    print(f"[DEBUG] Full image prompt: {full_prompt}")
    return full_prompt

def generate_illustration(full_prompt: str) -> str:
    """Generate illustration using Stability AI API"""
    stability_api_key = os.getenv('STABILITY_API_KEY')
    if not stability_api_key:
        raise HTTPException(status_code=500, detail="STABILITY_API_KEY not configured")
    
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    
    headers = {
        "Authorization": f"Bearer {stability_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "text_prompts": [
            {"text": full_prompt, "weight": 1},
            {"text": "color, colored, full color, grey background, gray background, colored background, busy background, detailed background, cluttered scene, complex background, noisy background, alien features, bizarre faces, distorted faces, weird proportions, monster, creature, non-human", "weight": -0.9}
        ],
        "cfg_scale": 7,
        "height": 896,
        "width": 1152,
        "samples": 1,
        "steps": 30
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        response_data = response.json()
        if "artifacts" not in response_data or len(response_data["artifacts"]) == 0:
            raise HTTPException(status_code=500, detail="No image artifacts in Stability AI response")
        
        # SDXL returns base64 encoded images in artifacts array
        import base64
        
        image_data = response_data["artifacts"][0]["base64"]
        
        # Return as data URL which can be processed by download_and_save_image
        return f"data:image/png;base64,{image_data}"
        
    except requests.exceptions.RequestException as e:
        print(f"Stability AI API error: {e}")
        raise HTTPException(status_code=500, detail=f"Stability AI API error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error in Stability AI generation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate illustration: {str(e)}")

def save_user_poem(poem_data: dict, prompt: str):
    # Get the next ID by finding the highest existing ID and adding 1
    try:
        with open(poems_path, "r") as f:
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

    with open(poems_path, "w") as f:
        json.dump(poems, f, indent=2)

def download_and_save_image(image_url: str, poem_id: str) -> str:
    """Process Stability AI data URL and save to static/images folder"""
    try:
        if not image_url.startswith('data:image'):
            raise ValueError("Expected data URL from Stability AI")
            
        # Handle data URL from Stability AI
        import base64
        header, data = image_url.split(',', 1)
        img_data = base64.b64decode(data)
        img = Image.open(BytesIO(img_data))
        
        # Ensure static/images directory exists
        images_dir = os.path.join(base_dir, "static", "images")
        os.makedirs(images_dir, exist_ok=True)
        
        # Save as PNG
        image_path = os.path.join(images_dir, f"{poem_id}.png")
        img.save(image_path, "PNG")
        
        return image_path
    except Exception as e:
        print(f"Error processing/saving image: {e}")
        raise e

@app.post("/generate", response_model=GenerateResponse)
async def generate_poem(request: GenerateRequest, background_tasks: BackgroundTasks):
    similar_poems = find_similar_poems(request.prompt)
    similar_poem_texts = [
        f"{poem['title']}\n{poem['content']}\n{poem['signature']}"
        for poem in similar_poems
    ]
    poem_data = generate_poem_with_openai(request.prompt, similar_poem_texts)

    # Determine the next numeric ID
    try:
        with open(poems_path, "r") as f:
            poems = json.load(f)
        next_id = max(poem["id"] for poem in poems) + 1 if poems else 1
    except FileNotFoundError:
        next_id = 1

    poem_data["similar_poems"] = similar_poems
    poem_data["poem_id"] = next_id  # Use numeric ID
    
    # Save the user poem to poems.json
    save_user_poem(poem_data, request.prompt)
    
    # Automatically start image generation in background
    def background_image_generation(poem_body, pid):
        try:
            visual_prompt = extract_visual_prompt(poem_body)
            full_prompt = combine_with_style(visual_prompt)
            illustration_url = generate_illustration(full_prompt)
            
            # Download and save the image
            image_path = download_and_save_image(illustration_url, str(pid))
            
            # Only update cache after file is successfully saved
            if os.path.exists(image_path):
                ILLUSTRATION_CACHE[str(pid)] = {
                    "illustration_prompt": visual_prompt,
                    "illustration_url": illustration_url
                }
                print(f"[Background Illustration Success]: Image saved to {image_path}")
            else:
                print(f"[Background Illustration Error]: File not found at {image_path}")
        except Exception as e:
            print(f"[Background Illustration Error]: {e}")
    
    background_tasks.add_task(background_image_generation, poem_data["body"], next_id)
    
    return GenerateResponse(**poem_data)


@app.get("/illustration")
async def get_illustration(poem_id: str):
    # Check if this is a classic poem by looking it up in poems.json
    try:
        with open(poems_path, "r") as f:
            poems = json.load(f)
        
        # Find the poem by ID
        poem = next((p for p in poems if str(p["id"]) == str(poem_id)), None)
        if poem and poem.get("type") == "classic":
            return {"status": "classic"}
    except Exception as e:
        print(f"Error checking poem type: {e}")
        # Continue to check for existing images even if type check fails
    
    # Check if image file already exists on disk
    image_path = os.path.join(base_dir, "static", "images", f"{poem_id}.png")
    if os.path.exists(image_path):
        return {"status": "ready", "illustration_url": f"/static/images/{poem_id}.png"}
    
    if poem_id not in ILLUSTRATION_CACHE:
        return {"status": "pending"}
    return {"status": "ready", **ILLUSTRATION_CACHE[poem_id]}

@app.get("/poems")
async def get_poems():
    """Get all archive poems"""
    try:
        with open(poems_path, "r") as f:
            poems = json.load(f)
        # Return poems in reverse order (newest first)
        poems_reversed = list(reversed(poems))
        return {"poems": poems_reversed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load poems: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def serve_root():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Index page not found")

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    index_path = os.path.join(static_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Page not found")