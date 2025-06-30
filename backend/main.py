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

# Sample poems for similarity search (hardcoded for now)
SAMPLE_POEMS = [
    {
        "title": "Tribute to a 'Subber Code'",
        "content": "For two weeks dow I'b had this code.\nA subber code! It's bery bad.\nA scratchy throat, a ruddy doze,\ned doebody seebs to udderstad\nbe wed I talk. I get doe sbiles or sybathy.\n(A leper has bore freds thad be.)\nBy ears are stuvved, I hack ed wheeze,\nI cough ed gasp, I sdiff ed sdeeze.\nI'b purchased ebery rebedy\nthe drug stores sell - frob A to Z.\nAspirid. Codact. Sidu-tabs.\nBicks idhalers. Pills ed caps-\nules. Duthig works. Dot chicked soup,\nor herbal tea; oradge juice or cadaloupe.\n\nEd writig poebs is tough edough,\nbut try it wed your doze is stuvved!\nDuthig seebs to rhybe today,\ned there's just wud thig I wad to say:\n\nPobes are bade by fools like be.\nWho write wed they're id bisery.\n\nAaaazcheeesh! Eduff. I quit this ode,\nby \"Tribute To A Subber Code.\"",
        "signature": "(J.D. Evans, a pseudonym, is a South Jersey writer who can pronounce\nthe letters 'n' and 'm' ... occasionally.)"
    },
    {
        "title": "Fatherhood's rewards; subtle, unending",
        "content": "Sigmund Freud was overjoyed\nwhen he tripped on the id and the ego.\nBut I was in heaven when my eldest turned seven\nand we paddled down the Oswego.\nAlfred Nobel was happy as hell\nwhen he stumbled on T.N.T.\nBut I had more fun when my five-year-old son\nplayed a toy drum recital for ME.\nWhen Einstein declared E was m times c squared\nhe felt giddy and Truth-struck no doubt.\nBut my spirit soars up when I lift the oars up\nand watch my two boys fish for trout.\nTed Turner turns gray and gets older each day\nas he measures his wealth in Atlanta.\nBut I own a treasure that stops time forever:\nthe letters my sons sent to Santa.\n\nFame can be fickle. Ambition's a tickle\nthat can turn into terminal itch.\nBut thanks to my progeny, one thing is clear to me:\non Life's bottom line, I am rich!",
        "signature": "(J.D. Evans, a pseudonym, is a South Jersey writer who yells at his sons\nwhen their bedrooms are a mess ... occasionally.)"
    },
    {
        "title": "Happiness is warm Zapper",
        "content": "I'd like to invent a pocket-sized Zapper\na portable, monogrammed laser-bushwacker.\nA painless and bloodless device I could use\nto \"eliminate\" (neatly) the people I choose.\n\n-\tOverweight drivers who swerve to the right\nbefore they turn left I would Zap with delight.\n-\tPeople at movies who chatter out loud\nI would Zap into atoms (if I were allowed.)\n-\tI'd Zap into vapors (if I had my way)\nall the zombies who tell me to \"have a nice day.\"\n-\tI'd Zap politicians and Howard Cosell,\nand unfunny people with dumb jokes to tell.\n-\tI'd Zap lines at banks and toll booths, of course.\nI'd Zap health food freaks without any remorse.\n-\tIf I saw a car that was parked on TWO spaces,\nI'd Zap car and driver. I wouldn't leave traces.\n\n-\tIf I had a Zapper I'd happily smite\nall the jerks who distract me when I try to write.\nBut one thought has soured this sweet fantasy:\nsuppose other people had Zappers like me,\nand one of them wanted to Zap and disperse\nanonymous authors of jangling verse ...\n\nBack to the drawing boards! Now I think twice,\nI'll develop an anti-Zap-Zapping device.",
        "signature": "(J.D. Evans, a pseudonym, is a South Jersey writer who makes left turns\nafter switching on his right directional signal ... occasionally.)"
    }
]

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
               "You often adopt parodic or whimsical variations of established forms (like nursery rhymes or T.S. Eliot’s The Waste Land)." 
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