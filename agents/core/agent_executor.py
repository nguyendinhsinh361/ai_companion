"""
Base Agent Executor for A2A Protocol
Implements the core execution logic for A2A-compliant agents
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import structlog

from a2a.server.agent_execution import AgentExecutor, RequestContext, EventQueue
from a2a.types import (
    Message,
    MessagePart,
    TextPart,
    Artifact,
    TaskUpdate,
    TaskUpdateType,
    MessageRole,
)

logger = structlog.get_logger(__name__)


class BaseAgentExecutor(AgentExecutor, ABC):
    """
    Base class for A2A agent executors
    Provides common functionality and structure for agent implementations
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent executor
        
        Args:
            name: Name of the agent
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.logger = logger.bind(agent=name)

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Main execution method for handling A2A requests
        
        Args:
            context: Request context containing message and metadata
            event_queue: Queue for sending events back to client
        """
        try:
            self.logger.info(
                "execute_start",
                task_id=context.task_id,
                message_id=context.message.message_id if context.message else None,
            )

            # Send initial status update
            await self._send_status_update(
                event_queue, 
                context.task_id, 
                "Processing request..."
            )

            # Extract user message
            user_message = self._extract_user_message(context)
            if not user_message:
                await self._send_error(
                    event_queue,
                    context.task_id,
                    "No valid message content found"
                )
                return

            # Process the message (implemented by subclass)
            response = await self.process_message(user_message, context)

            # Send response back to client
            await self._send_response(event_queue, context.task_id, response)

            self.logger.info("execute_complete", task_id=context.task_id)

        except Exception as e:
            self.logger.exception("execute_error", task_id=context.task_id, error=str(e))
            await self._send_error(event_queue, context.task_id, f"Execution error: {str(e)}")

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Handle task cancellation
        
        Args:
            context: Request context
            event_queue: Queue for sending events
        """
        self.logger.info("cancel_task", task_id=context.task_id)
        
        await event_queue.put(
            TaskUpdate(
                task_id=context.task_id,
                update_type=TaskUpdateType.CANCELED,
                message="Task canceled by user",
            )
        )

    @abstractmethod
    async def process_message(self, message: str, context: RequestContext) -> str:
        """
        Process the user message and generate a response
        Must be implemented by subclass
        
        Args:
            message: User's message text
            context: Request context
            
        Returns:
            Response text
        """
        pass

    def _extract_user_message(self, context: RequestContext) -> Optional[str]:
        """
        Extract text message from request context
        
        Args:
            context: Request context
            
        Returns:
            Extracted message text or None
        """
        if not context.message or not context.message.parts:
            return None

        # Find first text part
        for part in context.message.parts:
            if isinstance(part, TextPart):
                return part.text

        return None

    async def _send_status_update(
        self, 
        event_queue: EventQueue, 
        task_id: str, 
        status: str
    ) -> None:
        """
        Send a status update to the client
        
        Args:
            event_queue: Event queue
            task_id: Task ID
            status: Status message
        """
        await event_queue.put(
            TaskUpdate(
                task_id=task_id,
                update_type=TaskUpdateType.IN_PROGRESS,
                message=status,
            )
        )

    async def _send_response(
        self, 
        event_queue: EventQueue, 
        task_id: str, 
        response_text: str
    ) -> None:
        """
        Send final response to the client
        
        Args:
            event_queue: Event queue
            task_id: Task ID
            response_text: Response message
        """
        # Create response message
        response_message = Message(
            role=MessageRole.ASSISTANT,
            parts=[TextPart(text=response_text)],
        )

        # Send completion update
        await event_queue.put(
            TaskUpdate(
                task_id=task_id,
                update_type=TaskUpdateType.COMPLETED,
                message="Task completed successfully",
                result=response_message,
            )
        )

    async def _send_error(
        self, 
        event_queue: EventQueue, 
        task_id: str, 
        error_message: str
    ) -> None:
        """
        Send error response to the client
        
        Args:
            event_queue: Event queue
            task_id: Task ID
            error_message: Error message
        """
        await event_queue.put(
            TaskUpdate(
                task_id=task_id,
                update_type=TaskUpdateType.FAILED,
                message=error_message,
            )
        )


class StreamingAgentExecutor(BaseAgentExecutor):
    """
    Agent executor with streaming support
    Sends incremental updates as processing occurs
    """

    async def process_message_streaming(
        self, 
        message: str, 
        context: RequestContext,
        event_queue: EventQueue
    ) -> str:
        """
        Process message with streaming updates
        
        Args:
            message: User message
            context: Request context
            event_queue: Event queue for streaming updates
            
        Returns:
            Final response text
        """
        # Override this method to implement streaming
        return await self.process_message(message, context)

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Execute with streaming support
        """
        try:
            self.logger.info(
                "execute_streaming_start",
                task_id=context.task_id,
            )

            user_message = self._extract_user_message(context)
            if not user_message:
                await self._send_error(
                    event_queue,
                    context.task_id,
                    "No valid message content found"
                )
                return

            # Process with streaming
            response = await self.process_message_streaming(
                user_message, 
                context, 
                event_queue
            )

            # Send final response
            await self._send_response(event_queue, context.task_id, response)

            self.logger.info("execute_streaming_complete", task_id=context.task_id)

        except Exception as e:
            self.logger.exception("execute_streaming_error", error=str(e))
            await self._send_error(event_queue, context.task_id, str(e))