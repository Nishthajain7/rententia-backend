import json
import os
from typing import List
import uuid

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from google import genai
from pydantic import ValidationError

from app.crud.quiz_cache import store_quiz
from app.dependencies import get_current_user
from app.models import User
from app.schemas.quiz import QuizResponse, QuizQuestion, QuizQuestionSafe, Subject, QUIZ_RESPONSE_SCHEMA

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

@router.post("/generate-quiz", response_model=QuizResponse)
def generate_quiz(data: List[Subject], current_user: User = Depends(get_current_user)):
    
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
        questions = [QuizQuestion(**q) for q in quiz_data]
 
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
 
    quiz_id = str(uuid.uuid4())
    
    if not store_quiz(
        quiz_id=quiz_id,
        user_id=current_user.id,
        questions=[q.model_dump() for q in questions],
    ):
        raise HTTPException(
            status_code=503,
            detail="Quiz generated but could not be stored. Please try again."
        )
 
    safe_questions = [
        QuizQuestionSafe(
            question=q.question,
            options=q.options,
        ) for q in questions
    ]
 
    return QuizResponse(quiz_id=quiz_id, questions=safe_questions)