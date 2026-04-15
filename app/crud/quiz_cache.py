import json
import logging
from redis.exceptions import RedisError
from app.utils.redis_client import redis_client

logger = logging.getLogger(__name__)
QUIZ_TTL = 3600  # 60 mins

def store_quiz(quiz_id: str, user_id: int, questions: list):
    try:
        redis_client.setex(
            f"quiz:{quiz_id}",
            QUIZ_TTL,
            json.dumps({
                "user_id": user_id,
                "questions": questions
            })
        )
        return True
    
    except RedisError:
        logger.exception("Failed to cache quiz %s in Redis", quiz_id)
        return False