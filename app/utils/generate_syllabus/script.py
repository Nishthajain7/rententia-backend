import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Subject, Topic, Chapter, Concept

BASE_DIR = Path(__file__).resolve().parent
files = [
    BASE_DIR / "Physics.json",
    BASE_DIR / "Math.json",
    BASE_DIR / "Chemistry.json"
]

def populate():
    """
    Populate the db with syllabus from JSON files in the structure:
    Subject -> Topics -> Chapters -> Concepts
    """
    db: Session = SessionLocal()

    try:
        for file in files:
            with open(file, encoding="utf-8") as f:
                data = json.load(f)

            subject_name = data["subject"]
            subject = (db.query(Subject).filter(Subject.name == subject_name).first())
            
            if not subject:
                subject = Subject(name=subject_name)
                db.add(subject)
                db.flush()

            for topic_data in data["topics"]:
                topic_name = topic_data["topic"]
                topic = (db.query(Topic).filter(Topic.name == topic_name,).first())

                if not topic:
                    topic = Topic(name=topic_name, subject_id=subject.id)
                    db.add(topic)
                    db.flush()

                for chapter_data in topic_data["chapters"]:
                    chapter_name = chapter_data["name"]                    
                    chapter = (db.query(Chapter).filter(Chapter.name == chapter_name,).first())

                    if not chapter:
                        chapter = Chapter(name=chapter_name, topic_id=topic.id)
                        db.add(chapter)
                        db.flush()

                    for concept_name in chapter_data["concepts"]:
                        concept = (db.query(Concept).filter(
                            Concept.name == concept_name).first())
                        
                        if not concept:
                            concept = Concept(name=concept_name,chapter_id=chapter.id)
                            db.add(concept)
                            
            db.commit()

    except Exception:
        db.rollback()
        raise
    
    finally:
        db.close()

if __name__ == "__main__":
    populate()