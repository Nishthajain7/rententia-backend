import json
import os
from typing import List

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from google import genai
from pydantic import ValidationError

from app.schemas.quiz import QuizQuestion, Subject, QUIZ_RESPONSE_SCHEMA

load_dotenv()

def get_genai_client():
    api_key = os.getenv("GEMINI_API")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API is not configured"
        )
    return genai.Client(api_key=api_key)

router = APIRouter(prefix="/quiz", tags=["Quiz"])

@router.post("/generate-quiz", response_model=List[QuizQuestion])
def generate_quiz(data: List[Subject]):
    
    client = get_genai_client()
    syllabus_text = ""

    for subject in data:
        syllabus_text += f"\n{subject.subject}\n"
        
        for ch in subject.chapters:
            concepts = ", ".join(ch.concepts)
            syllabus_text += f"- Chapter: {ch.chapter}\n"
            syllabus_text += f"  Concepts: {concepts}\n"

    prompt = f"""
Generate MCQ questions from the JEE syllabus given below
{syllabus_text}

Rules:
- Each question must have only 1 correct answer.
- Do NOT invent chapters or concepts.
- The chapter and related_concepts must come from the syllabus above.
"""
    
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": QUIZ_RESPONSE_SCHEMA
        }
    )
        
    try:
        quiz_data = json.loads(response.text)
        return [QuizQuestion(**q) for q in quiz_data]

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Model returned invalid JSON format"
        )

    except ValidationError:
        raise HTTPException(
            status_code=500,
            detail="Model returned invalid data structure"
        )