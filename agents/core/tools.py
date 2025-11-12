"""
Tool Registry and Management
Manages available tools for A2A agents
"""

from typing import Dict, Any, Callable, List, Optional
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ToolDefinition:
    """Definition of an agent tool"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ToolRegistry:
    """
    Registry for managing agent tools
    """

    def __init__(self):
        """Initialize the tool registry"""
        self.tools: Dict[str, ToolDefinition] = {}
        self.logger = logger.bind(component="tool_registry")

    def register(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        """
        Register a new tool
        
        Args:
            name: Tool name
            description: Tool description
            function: Tool function
            parameters: Tool parameters schema
            tags: Tool tags for categorization
        """
        tool = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters or {},
            function=function,
            tags=tags or [],
        )
        
        self.tools[name] = tool
        self.logger.info("tool_registered", tool_name=name)

    def decorator(
        self,
        name: str,
        description: str,
        parameters: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ):
        """
        Decorator for registering tools
        
        Args:
            name: Tool name
            description: Tool description
            parameters: Tool parameters schema
            tags: Tool tags
            
        Returns:
            Decorator function
        """
        def wrapper(func: Callable) -> Callable:
            self.register(name, description, func, parameters, tags)
            return func
        return wrapper

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """
        Get a tool by name
        
        Args:
            name: Tool name
            
        Returns:
            ToolDefinition or None
        """
        return self.tools.get(name)

    def get_all_tools(self) -> Dict[str, ToolDefinition]:
        """
        Get all registered tools
        
        Returns:
            Dictionary of all tools
        """
        return self.tools.copy()

    def get_tools_by_tag(self, tag: str) -> List[ToolDefinition]:
        """
        Get tools by tag
        
        Args:
            tag: Tag to filter by
            
        Returns:
            List of matching tools
        """
        return [
            tool for tool in self.tools.values()
            if tag in tool.tags
        ]

    def execute_tool(self, name: str, **kwargs) -> Any:
        """
        Execute a tool by name
        
        Args:
            name: Tool name
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        
        try:
            self.logger.info("tool_execute_start", tool_name=name)
            result = tool.function(**kwargs)
            self.logger.info("tool_execute_complete", tool_name=name)
            return result
        except Exception as e:
            self.logger.exception("tool_execute_error", tool_name=name, error=str(e))
            raise

    async def execute_tool_async(self, name: str, **kwargs) -> Any:
        """
        Execute an async tool by name
        
        Args:
            name: Tool name
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        
        try:
            self.logger.info("tool_execute_async_start", tool_name=name)
            result = await tool.function(**kwargs)
            self.logger.info("tool_execute_async_complete", tool_name=name)
            return result
        except Exception as e:
            self.logger.exception("tool_execute_async_error", tool_name=name, error=str(e))
            raise

    def unregister(self, name: str) -> bool:
        """
        Unregister a tool
        
        Args:
            name: Tool name
            
        Returns:
            True if tool was removed, False if not found
        """
        if name in self.tools:
            del self.tools[name]
            self.logger.info("tool_unregistered", tool_name=name)
            return True
        return False

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Get OpenAI-compatible tool schemas
        
        Returns:
            List of tool schemas
        """
        schemas = []
        
        for tool in self.tools.values():
            schema = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
            }
            schemas.append(schema)
        
        return schemas

    def get_langchain_tools(self) -> List[Any]:
        """
        Convert tools to LangChain format
        
        Returns:
            List of LangChain tools
        """
        try:
            from langchain.tools import Tool
            
            langchain_tools = []
            
            for tool in self.tools.values():
                lc_tool = Tool(
                    name=tool.name,
                    description=tool.description,
                    func=tool.function,
                )
                langchain_tools.append(lc_tool)
            
            return langchain_tools
        except ImportError:
            self.logger.error("langchain_not_installed")
            return []

    def __len__(self) -> int:
        """Return number of registered tools"""
        return len(self.tools)

    def __contains__(self, name: str) -> bool:
        """Check if tool is registered"""
        return name in self.tools


# Global tool registry instance
default_registry = ToolRegistry()


# Convenience functions using default registry
def register_tool(
    name: str,
    description: str,
    function: Callable,
    parameters: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
) -> None:
    """Register a tool in the default registry"""
    default_registry.register(name, description, function, parameters, tags)


def tool(
    name: str,
    description: str,
    parameters: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
):
    """Decorator for registering tools in default registry"""
    return default_registry.decorator(name, description, parameters, tags)


def get_tool(name: str) -> Optional[ToolDefinition]:
    """Get a tool from the default registry"""
    return default_registry.get_tool(name)


def execute_tool(name: str, **kwargs) -> Any:
    """Execute a tool from the default registry"""
    return default_registry.execute_tool(name, **kwargs)