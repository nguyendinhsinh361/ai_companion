"""
Agent Card Creation
Utilities for creating A2A-compliant agent cards
"""

from typing import List, Optional
from a2a.types import (
    AgentCard,
    AgentSkill,
    InputMode,
    OutputMode,
    Contact,
)


def create_agent_card(
    name: str,
    description: str,
    version: str,
    skills: List[AgentSkill],
    url: Optional[str] = None,
    contact: Optional[Contact] = None,
    tags: Optional[List[str]] = None,
) -> AgentCard:
    """
    Create an A2A-compliant agent card
    
    Args:
        name: Agent name
        description: Agent description
        version: Agent version
        skills: List of agent skills
        url: Optional agent URL
        contact: Optional contact information
        tags: Optional list of tags
        
    Returns:
        AgentCard instance
    """
    return AgentCard(
        name=name,
        description=description,
        version=version,
        skills=skills,
        url=url,
        contact=contact,
        tags=tags or [],
    )


def create_basic_skill(
    skill_id: str,
    name: str,
    description: str,
    examples: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
) -> AgentSkill:
    """
    Create a basic agent skill with text input/output
    
    Args:
        skill_id: Unique skill identifier
        name: Skill name
        description: Skill description
        examples: Example prompts/queries
        tags: Skill tags for categorization
        
    Returns:
        AgentSkill instance
    """
    return AgentSkill(
        id=skill_id,
        name=name,
        description=description,
        examples=examples or [],
        tags=tags or [],
        input_modes=[InputMode.TEXT],
        output_modes=[OutputMode.TEXT],
    )


def create_rag_skill(
    skill_id: str = "rag_query",
    name: str = "Document RAG Query",
    description: str = "Query documents using RAG (Retrieval-Augmented Generation)",
    examples: Optional[List[str]] = None,
) -> AgentSkill:
    """
    Create a RAG-specific skill
    
    Args:
        skill_id: Skill ID
        name: Skill name
        description: Skill description
        examples: Example queries
        
    Returns:
        AgentSkill configured for RAG operations
    """
    default_examples = [
        "What information is available about X?",
        "Find documents related to Y",
        "Summarize the content about Z",
    ]
    
    return AgentSkill(
        id=skill_id,
        name=name,
        description=description,
        examples=examples or default_examples,
        tags=["rag", "retrieval", "search", "documents"],
        input_modes=[InputMode.TEXT],
        output_modes=[OutputMode.TEXT],
    )


def create_conversational_skill(
    skill_id: str = "conversation",
    name: str = "Conversational Assistant",
    description: str = "General conversation and question answering",
    examples: Optional[List[str]] = None,
) -> AgentSkill:
    """
    Create a conversational skill
    
    Args:
        skill_id: Skill ID
        name: Skill name
        description: Skill description
        examples: Example queries
        
    Returns:
        AgentSkill configured for conversation
    """
    default_examples = [
        "Hello, how are you?",
        "Can you help me with...?",
        "Tell me about...",
    ]
    
    return AgentSkill(
        id=skill_id,
        name=name,
        description=description,
        examples=examples or default_examples,
        tags=["conversation", "chat", "qa"],
        input_modes=[InputMode.TEXT],
        output_modes=[OutputMode.TEXT],
    )


def create_multimodal_skill(
    skill_id: str,
    name: str,
    description: str,
    input_modes: List[InputMode],
    output_modes: List[OutputMode],
    examples: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
) -> AgentSkill:
    """
    Create a multimodal skill with custom input/output modes
    
    Args:
        skill_id: Skill ID
        name: Skill name
        description: Skill description
        input_modes: List of supported input modes
        output_modes: List of supported output modes
        examples: Example queries
        tags: Skill tags
        
    Returns:
        AgentSkill with specified modes
    """
    return AgentSkill(
        id=skill_id,
        name=name,
        description=description,
        examples=examples or [],
        tags=tags or [],
        input_modes=input_modes,
        output_modes=output_modes,
    )


# Example Agent Card Configurations

def create_rag_agent_card(
    name: str = "RAG Agent",
    version: str = "1.0.0",
    url: Optional[str] = None,
) -> AgentCard:
    """
    Create a pre-configured RAG agent card
    
    Args:
        name: Agent name
        version: Agent version
        url: Agent URL
        
    Returns:
        AgentCard configured for RAG operations
    """
    skills = [
        create_rag_skill(),
        create_conversational_skill(),
    ]
    
    return create_agent_card(
        name=name,
        description="A RAG-powered agent that can query and retrieve information from documents",
        version=version,
        skills=skills,
        url=url,
        tags=["rag", "retrieval", "documents", "qa"],
    )


def create_langchain_agent_card(
    name: str = "LangChain Agent",
    version: str = "1.0.0",
    url: Optional[str] = None,
) -> AgentCard:
    """
    Create a pre-configured LangChain agent card
    
    Args:
        name: Agent name
        version: Agent version
        url: Agent URL
        
    Returns:
        AgentCard configured for LangChain operations
    """
    skills = [
        create_basic_skill(
            skill_id="langchain_qa",
            name="Question Answering",
            description="Answer questions using LangChain and LLMs",
            examples=[
                "What is the capital of France?",
                "Explain quantum computing",
                "How does photosynthesis work?",
            ],
            tags=["qa", "langchain", "llm"],
        ),
        create_basic_skill(
            skill_id="langchain_tool_use",
            name="Tool Usage",
            description="Execute tasks using various tools via LangChain",
            examples=[
                "Search the web for information about X",
                "Calculate 45 * 67",
                "Get the current weather",
            ],
            tags=["tools", "langchain", "execution"],
        ),
    ]
    
    return create_agent_card(
        name=name,
        description="An intelligent agent powered by LangChain and LLMs",
        version=version,
        skills=skills,
        url=url,
        tags=["langchain", "llm", "tools", "agent"],
    )