from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
from openai import OpenAI

app = FastAPI(title="Vel-Kural Moral Story Agent API")

# Load Dataset for RAG
# Handle potential relative paths (local run vs docker run)
DATASET_PATH = os.path.join(os.path.dirname(__file__), "data", "KURAL_DATASET.csv")
if not os.path.exists(DATASET_PATH):
    DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "KURAL_DATASET.csv")

try:
    df = pd.read_csv(DATASET_PATH)
except Exception as e:
    df = None
    print(f"Warning: Could not load dataset at {DATASET_PATH}. Error: {e}")

# Initialize OpenAI Client (Requires OPENAI_API_KEY environment variable)
try:
    client = OpenAI()
except Exception as e:
    client = None
    print("Warning: OpenAI client could not initialize. Ensure OPENAI_API_KEY is set.")

class StoryRequest(BaseModel):
    kural_number: int

@app.get("/")
def read_root():
    return {"message": "Welcome to the Vel-Kural API. Use the /generate_story endpoint."}

@app.post("/generate_story")
def generate_story(request: StoryRequest):
    if df is None:
        raise HTTPException(status_code=500, detail="Thirukkural dataset could not be loaded by the backend.")
    if client is None:
        raise HTTPException(status_code=500, detail="OpenAI configuration is missing.")
        
    try:
        # Kurals in the dataset are indexed from 1 to 1330 sequentially
        # The first row corresponds to kural_number 1 (index 0)
        row = df.iloc[request.kural_number - 1]
    except IndexError:
        raise HTTPException(status_code=404, detail="Kural not found. Ensure the number is between 1 and 1330.")

    tamil_verse = row.get('TAMIL_VERSE', '')
    tamil_meaning = row.get('TAMIL_EXPLANATION', '')
    english_verse = row.get('ENGLISH_VERSE', '')
    english_meaning = row.get('ENGLISH_EXPLANATION', '')

    prompt = f"""
    You are an expert storyteller, cultural historian, and moral philosopher. 
    I will provide you with a specific verse from the ancient Thirukkural and its meaning.
    
    Thirukkural (Tamil): {tamil_verse}
    Meaning (Tamil): {tamil_meaning}
    
    Thirukkural (English): {english_verse}
    Meaning (English): {english_meaning}
    
    Based purely on the core message of this specific verse, please generate TWO distinct, captivating narrative moral stories. 
    Each story MUST be approximately 1000 words long. They should use rich vocabulary and compelling storytelling techniques.
    
    1. A beautiful, captivating moral story in English (approx 1000 words).
    2. A beautiful, captivating moral story in Tamil (approx 1000 வார்த்தைகள்).
    
    Format your response clearly. Separate them using EXACTLY the following markers on their own lines:
    ===ENGLISH STORY===
    ===TAMIL STORY===
    """

    try:
        # Generate the stories utilizing the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4", # Using GPT-4 for better creative writing capabilities
            messages=[
                {"role": "system", "content": "You are a master storyteller who weaves engaging narrative tales inspired by ancient literary wisdom."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=6000 # Give plenty of tokens for 2000 total words
        )
        
        full_text = response.choices[0].message.content
        
        # Extract the stories based on the delimiters
        english_story = ""
        tamil_story = ""
        
        if "===ENGLISH STORY===" in full_text and "===TAMIL STORY===" in full_text:
            parts = full_text.split("===TAMIL STORY===")
            english_part = parts[0].replace("===ENGLISH STORY===", "").strip()
            tamil_part = parts[1].strip()
            english_story = english_part
            tamil_story = tamil_part
        else:
            english_story = "Notice: The model did not correctly format the output separators. Here is the raw response:\n\n" + full_text
            tamil_story = ""

        return {
            "english_story": english_story,
            "tamil_story": tamil_story
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating story from OpenAI: {str(e)}")
