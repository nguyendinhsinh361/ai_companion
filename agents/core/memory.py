"""
Agent Memory Management
Handles conversation history and context for A2A agents
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog

from a2a.types import Message, MessageRole

logger = structlog.get_logger(__name__)


class AgentMemory:
    """
    Manages conversation history and context for agents
    """

    def __init__(self, max_messages: int = 100):
        """
        Initialize agent memory
        
        Args:
            max_messages: Maximum number of messages to retain
        """
        self.max_messages = max_messages
        self.messages: List[Message] = []
        self.metadata: Dict[str, Any] = {}
        self.logger = logger.bind(component="agent_memory")

    def add_message(self, message: Message) -> None:
        """
        Add a message to memory
        
        Args:
            message: Message to add
        """
        self.messages.append(message)
        
        # Trim if exceeds max
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        
        self.logger.debug(
            "message_added",
            role=message.role,
            total_messages=len(self.messages),
        )

    def get_messages(
        self, 
        last_n: Optional[int] = None,
        role: Optional[MessageRole] = None,
    ) -> List[Message]:
        """
        Retrieve messages from memory
        
        Args:
            last_n: Optional number of recent messages to retrieve
            role: Optional filter by message role
            
        Returns:
            List of messages
        """
        messages = self.messages
        
        # Filter by role if specified
        if role:
            messages = [m for m in messages if m.role == role]
        
        # Get last N messages
        if last_n:
            messages = messages[-last_n:]
        
        return messages

    def get_conversation_history(self) -> str:
        """
        Get formatted conversation history as string
        
        Returns:
            Formatted conversation history
        """
        history_parts = []
        
        for msg in self.messages:
            role = msg.role.value if hasattr(msg.role, 'value') else str(msg.role)
            
            # Extract text from message parts
            text_parts = []
            if msg.parts:
                for part in msg.parts:
                    if hasattr(part, 'text'):
                        text_parts.append(part.text)
            
            if text_parts:
                history_parts.append(f"{role}: {' '.join(text_parts)}")
        
        return "\n\n".join(history_parts)

    def clear(self) -> None:
        """Clear all messages from memory"""
        self.messages.clear()
        self.logger.info("memory_cleared")

    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata value
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics
        
        Returns:
            Dictionary with memory stats
        """
        return {
            "total_messages": len(self.messages),
            "max_messages": self.max_messages,
            "user_messages": len([m for m in self.messages if m.role == MessageRole.USER]),
            "assistant_messages": len([m for m in self.messages if m.role == MessageRole.ASSISTANT]),
            "metadata_keys": list(self.metadata.keys()),
        }


class RedisBackedMemory(AgentMemory):
    """
    Agent memory backed by Redis for persistence
    """

    def __init__(
        self, 
        redis_client: Any,
        session_id: str,
        max_messages: int = 100,
        ttl: int = 3600,
    ):
        """
        Initialize Redis-backed memory
        
        Args:
            redis_client: Redis client instance
            session_id: Session identifier
            max_messages: Maximum messages to retain
            ttl: Time to live in seconds
        """
        super().__init__(max_messages)
        self.redis_client = redis_client
        self.session_id = session_id
        self.ttl = ttl
        self.key_prefix = f"agent_memory:{session_id}"
        
        # Load existing messages from Redis
        self._load_from_redis()

    def _load_from_redis(self) -> None:
        """Load messages from Redis"""
        try:
            # Implementation depends on your Redis schema
            # This is a placeholder
            pass
        except Exception as e:
            self.logger.error("redis_load_error", error=str(e))

    def _save_to_redis(self) -> None:
        """Save messages to Redis"""
        try:
            # Implementation depends on your Redis schema
            # This is a placeholder
            pass
        except Exception as e:
            self.logger.error("redis_save_error", error=str(e))

    def add_message(self, message: Message) -> None:
        """
        Add message and persist to Redis
        
        Args:
            message: Message to add
        """
        super().add_message(message)
        self._save_to_redis()

    def clear(self) -> None:
        """Clear messages from memory and Redis"""
        super().clear()
        try:
            # Clear from Redis
            keys = self.redis_client.keys(f"{self.key_prefix}:*")
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            self.logger.error("redis_clear_error", error=str(e))