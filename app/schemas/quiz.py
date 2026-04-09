from typing import List
from pydantic import BaseModel, Field

class Chapter(BaseModel):
    chapter: str
    concepts: List[str]
    
class Subject(BaseModel):
    subject: str
    chapters: List[Chapter]
    
class QuizQuestion(BaseModel):
    chapter: str
    question: str
    options: List[str] = Field(min_length=4, max_length=4)
    correct_answer: str
    related_concepts: List[str]
        
QUIZ_RESPONSE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "chapter": {"type": "string"},
            "question": {"type": "string"},
            "options": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 4,
                "maxItems": 4
            },
            "correct_answer": {"type": "string"},
            "related_concepts": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": [
            "chapter",
            "question",
            "options",
            "correct_answer",
            "related_concepts"
        ]
    }
}