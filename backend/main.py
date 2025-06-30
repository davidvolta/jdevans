from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from typing import List

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

class GenerateRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    poem: str
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
        similar_poems.append(f"Title: {poem['title']}\n{poem['content']}\n{poem['signature']}")
    
    return similar_poems

def generate_mock_poem(prompt: str, similar_poems: List[str]) -> str:
    """Generate a mock poem based on the prompt and similar poems."""
    # This is a placeholder - in the real implementation, this would call OpenAI API
    mock_poem = f"""Mock Poem for: "{prompt}"


The {prompt.lower()} sits there, mocking me,
A challenge that I cannot see.
I try and try, but all in vain,
The {prompt.lower()} drives me quite insane.

Perhaps tomorrow I'll succeed,
Or maybe I'll plant a different seed.
For now I'll sit and contemplate,
The mysteries of {prompt.lower()}'s fate.

(J.D. Evans, a pseudonym, is a New Jersey writer who contemplates {prompt.lower()} ... occasionally.)"""
    
    return mock_poem

@app.post("/generate", response_model=GenerateResponse)
async def generate_poem(request: GenerateRequest):
    try:
        # Find similar poems
        similar_poems = find_similar_poems(request.prompt)
        
        # Generate mock poem (replace with actual OpenAI call later)
        generated_poem = generate_mock_poem(request.prompt, similar_poems)
        
        return GenerateResponse(
            poem=generated_poem,
            similar_poems=similar_poems
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "J.D. Evans Poem Generator API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 