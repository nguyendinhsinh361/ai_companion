"""
A2A Agent Service
Main application for running A2A-compliant agents
"""

import os
import asyncio
from typing import Optional
import structlog

from a2a.server.http import create_a2a_server
from a2a.types import AgentCard

from core.agent_card import create_rag_agent_card, create_langchain_agent_card
from examples.simple_agent import SimpleAgentExecutor
from examples.rag_agent import RAGAgentExecutor

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class A2AAgentService:
    """
    A2A Agent Service
    Manages the A2A server and agent executors
    """

    def __init__(
        self,
        agent_type: str = "simple",
        host: str = "0.0.0.0",
        port: int = 8000,
    ):
        """
        Initialize the A2A Agent Service
        
        Args:
            agent_type: Type of agent to run (simple, rag, langchain)
            host: Server host
            port: Server port
        """
        self.agent_type = agent_type
        self.host = host
        self.port = port
        self.logger = logger.bind(
            agent_type=agent_type,
            host=host,
            port=port,
        )

    def create_agent_card(self) -> AgentCard:
        """
        Create agent card based on agent type
        
        Returns:
            AgentCard instance
        """
        url = f"http://{self.host}:{self.port}"
        
        if self.agent_type == "rag":
            return create_rag_agent_card(
                name="RAG Agent",
                version="1.0.0",
                url=url,
            )
        elif self.agent_type == "langchain":
            return create_langchain_agent_card(
                name="LangChain Agent",
                version="1.0.0",
                url=url,
            )
        else:
            # Simple agent
            from core.agent_card import create_agent_card, create_conversational_skill
            
            return create_agent_card(
                name="Simple Agent",
                description="A simple A2A agent that echoes messages",
                version="1.0.0",
                skills=[create_conversational_skill()],
                url=url,
                tags=["simple", "demo"],
            )

    def create_agent_executor(self):
        """
        Create agent executor based on agent type
        
        Returns:
            Agent executor instance
        """
        if self.agent_type == "rag":
            return RAGAgentExecutor(
                name="rag_agent",
                config={
                    "vector_store_url": os.getenv("QDRANT_URL", "http://localhost:6333"),
                    "collection_name": os.getenv("QDRANT_COLLECTION", "documents"),
                }
            )
        elif self.agent_type == "langchain":
            # Placeholder - implement LangChain agent
            return SimpleAgentExecutor(name="langchain_agent")
        else:
            return SimpleAgentExecutor(name="simple_agent")

    async def start(self):
        """
        Start the A2A server
        """
        self.logger.info("starting_a2a_service")

        try:
            # Create agent card and executor
            agent_card = self.create_agent_card()
            agent_executor = self.create_agent_executor()

            # Create A2A server
            server = create_a2a_server(
                agent_card=agent_card,
                agent_executor=agent_executor,
                host=self.host,
                port=self.port,
            )

            self.logger.info(
                "a2a_service_started",
                agent_name=agent_card.name,
                url=agent_card.url,
            )

            # Run the server
            import uvicorn
            config = uvicorn.Config(
                server,
                host=self.host,
                port=self.port,
                log_level="info",
            )
            server_instance = uvicorn.Server(config)
            await server_instance.serve()

        except Exception as e:
            self.logger.exception("a2a_service_error", error=str(e))
            raise


def main():
    """
    Main entry point
    """
    # Configuration from environment
    agent_type = os.getenv("AGENT_TYPE", "simple")
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    # Create and start service
    service = A2AAgentService(
        agent_type=agent_type,
        host=host,
        port=port,
    )

    # Run async event loop
    asyncio.run(service.start())


if __name__ == "__main__":
    main()