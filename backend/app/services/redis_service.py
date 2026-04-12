"""Redis service for deduplication and caching."""
import redis
from typing import Optional
import hashlib
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class RedisService:
    """Service for Redis operations"""

    _client: Optional[redis.Redis] = None

    @classmethod
    def get_client(cls) -> Optional[redis.Redis]:
        """Get Redis client instance (singleton)"""
        if cls._client is None:
            try:
                cls._client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_timeout=2,
                    socket_connect_timeout=2
                )
                # Test connection
                cls._client.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")
                cls._client = None
        return cls._client

    @classmethod
    def check_and_mark_sent(
        cls,
        message_id: str,
        ttl_seconds: int = 604800  # 7 days
    ) -> bool:
        """
        Check if a message was already sent and mark it as sent.

        This is an atomic operation using Redis SET with NX (not exists).
        Returns True if the message was NOT sent before (safe to send).
        Returns False if the message was already sent (duplicate).

        Args:
            message_id: Unique message identifier
            ttl_seconds: Time to keep the record (default: 7 days)

        Returns:
            bool: True if message can be sent (not a duplicate), False if duplicate
        """
        client = cls.get_client()
        if not client:
            # Redis unavailable - log warning but allow send
            logger.warning(f"Redis unavailable - cannot check duplicate for {message_id}")
            return True  # Fail open: allow send if Redis is down

        try:
            # SET key value NX EX ttl
            # NX = set only if key doesn't exist (atomic check-and-set)
            # Returns True if key was set (new), False if key already existed (duplicate)
            key = f"email:sent:{message_id}"
            result = client.set(key, "1", ex=ttl_seconds, nx=True)

            if result:
                logger.info(f"Message {message_id} marked as sent")
                return True  # Not a duplicate
            else:
                logger.warning(f"Duplicate send attempt detected for {message_id}")
                return False  # Duplicate

        except Exception as e:
            logger.error(f"Redis error checking duplicate: {e}")
            return True  # Fail open: allow send if Redis has errors

    @classmethod
    def generate_message_id(
        cls,
        user_id: str,
        lead_id: str,
        subject: str,
        body: str,
        context: str = ""
    ) -> str:
        """
        Generate a unique message ID based on recipients content.

        This creates a deterministic hash so that identical emails
        get the same message_id, enabling deduplication.

        Args:
            user_id: User ID
            lead_id: Lead/recipient ID
            subject: Email subject
            body: Email body
            context: Optional extra dedupe context (e.g., campaign_id:step_index)

        Returns:
            str: Unique message ID (hex hash)
        """
        # Create deterministic hash from email components
        content = f"{user_id}:{lead_id}:{subject}:{body}:{context}"
        hash_obj = hashlib.sha256(content.encode('utf-8'))
        message_id = hash_obj.hexdigest()[:32]  # First 32 chars
        return message_id

    @classmethod
    def clear_sent_message(cls, message_id: str) -> bool:
        """
        Clear a sent message from Redis (for testing/recovery).

        Args:
            message_id: Message ID to clear

        Returns:
            bool: True if cleared
        """
        client = cls.get_client()
        if not client:
            return False

        try:
            key = f"email:sent:{message_id}"
            result = client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis error clearing message: {e}")
            return False

    @classmethod
    def get_sent_count(cls) -> int:
        """
        Get count of tracked sent messages (for monitoring).

        Returns:
            int: Number of messages in Redis
        """
        client = cls.get_client()
        if not client:
            return 0

        try:
            # Count keys matching pattern
            keys = client.keys("email:sent:*")
            return len(keys)
        except Exception as e:
            logger.error(f"Redis error counting messages: {e}")
            return 0
