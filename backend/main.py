from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from typing import List
import os
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="J.D. Evans Poem Generator API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("poems.json", "r") as f:
    SAMPLE_POEMS = json.load(f)

# Create TF-IDF vectorizer for similarity search
vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
poem_texts = [f"{poem['title']} {poem['content']}" for poem in SAMPLE_POEMS]
tfidf_matrix = vectorizer.fit_transform(poem_texts)

client = OpenAI()

class GenerateRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    title: str
    body: str
    signature: str
    similar_poems: List[str]

def find_similar_poems(prompt: str, top_k: int = 2) -> List[str]:
    """Find the most similar poems to the given prompt using cosine similarity."""
    prompt_vector = vectorizer.transform([prompt])
    similarities = cosine_similarity(prompt_vector, tfidf_matrix).flatten()
    
    # Get indices of top similar poems
    top_indices = similarities.argsort()[-top_k:][::-1]
    print(f"[DEBUG] Vectorizer selected poem IDs: {[SAMPLE_POEMS[int(i)]['id'] for i in top_indices]}")
    
    similar_poems = []
    for idx in top_indices:
        poem = SAMPLE_POEMS[idx]
        similar_poems.append(f"{poem['title']}\n{poem['content']}\n{poem['signature']}")
    
    return similar_poems

def generate_poem_with_openai(prompt: str, similar_poems: List[str]) -> dict:
    print("Starting OpenAI poem generation...")
    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": (
               "You are J.D. Evans, a clever and heartfelt South Jersey newspaper columnist and poet."
               "Your poems are short, humorous, occasionally satirical or poignant reflections on everyday American life that often use unexpected metaphors."
               "Your tone is conversational, self-deprecating, observational, and moral, with a wry or bittersweet undercurrent. You frequently write in formal rhyme and meter—especially rhymed couplets and quatrains in anapestic or iambic meter—but sometimes break meter or form for comedic or dramatic effect."
               "Your work references cultural touchpoints from 1980s America: Reaganomics, the Cold War, Miss America pageants, soap operas, casino life, barbecues, family routines, public schooling, and politics." 
               "You often adopt parodic or whimsical variations of established forms (like nursery rhymes or T.S. Eliot's The Waste Land)." 
               "Your poems ALWAYS end with a humorous biographical signature related to the poem in the form '(J.D. Evans, a pseudonym, is [statement related to poem]  … occasionally)'."
               "Always sign your poems with a version of this line."
               "Generate poems in this style—playful, reflective, and rhythmically engaging—grounded in the ordinary absurdities of American life."
            )
        },
        {
            "role": "user",
            "content": (
                f"Write a poem inspired by the following theme: {prompt}.\n\n"
                f"Here are some past poems for style inspiration:\n\n" +
                "\n\n---\n\n".join(similar_poems) +
                "\n\nReturn the result as a JSON object with the following fields:\n"
                "{\n"
                '  "title": "The title of the poem",\n'
                '  "body": "The poem body, with line breaks as \\n",\n'
                '  "signature": "The signature line, e.g. (J.D. Evans, ...)"\n'
                "}\n"
                "Do not include any text outside the JSON object."
            )
        }
    ]
    print("Messages prepared, calling OpenAI...")
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.85,
            max_tokens=500
        )
        print("OpenAI response received")
        if response.choices and response.choices[0].message and response.choices[0].message.content:
            content = response.choices[0].message.content.strip()
            print(f"OpenAI raw content: {content}")
            import json
            try:
                poem_json = json.loads(content)
                return poem_json
            except Exception as e:
                print(f"JSON parse error: {e}")
                return {"title": "Error", "body": content, "signature": "", "similar_poems": similar_poems}
        else:
            print("No content in OpenAI response")
            return {"title": "Error", "body": "[OpenAI API Error]: No content returned from OpenAI.", "signature": "", "similar_poems": similar_poems}
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return {"title": "Error", "body": f"[OpenAI API Error]: {e}", "signature": "", "similar_poems": similar_poems}

@app.post("/generate", response_model=GenerateResponse)
async def generate_poem(request: GenerateRequest):
    try:
        print(f"Received request for prompt: {request.prompt}")
        print("Finding similar poems...")
        similar_poems = find_similar_poems(request.prompt)
        print(f"Found {len(similar_poems)} similar poems")
        print("Calling OpenAI API...")
        poem_data = generate_poem_with_openai(request.prompt, similar_poems)
        print("OpenAI call completed")
        poem_data["similar_poems"] = similar_poems
        return GenerateResponse(**poem_data)
    except Exception as e:
        print(f"Error in generate_poem: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "J.D. Evans Poem Generator API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 

@app.get("/debug")
async def debug_similarity(prompt: str):
    prompt_vector = vectorizer.transform([prompt])
    similarities = cosine_similarity(prompt_vector, tfidf_matrix).flatten()
    top_indices = similarities.argsort()[::-1]

    results = []
    for idx in top_indices:
        poem = SAMPLE_POEMS[int(idx)]  # explicitly cast
        score = similarities[idx]
        contains_word = "skiing" in poem["content"].lower()
        results.append({
            "id": poem.get("id", int(idx)),  # ✅ Use real poem ID if present
            "title": poem["title"],
            "score": float(score),
            "contains_prompt_word": contains_word,
            "snippet": poem["content"][:100] + "..."
        })

    return {
        "prompt": prompt,
        "results": results[:10]
    }

