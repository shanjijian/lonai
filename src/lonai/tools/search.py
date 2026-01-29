"""Search tool using Tavily API."""

import logging
from typing import Any, Dict, List, Literal, Optional

from tavily import TavilyClient

from lonai.config.constants import SearchTopic

logger = logging.getLogger(__name__)


class SearchTool:
    """Search tool for conducting internet searches using Tavily."""
    
    def __init__(self, api_key: str, max_results: int = 5):
        """Initialize search tool.
        
        Args:
            api_key: Tavily API key
            max_results: Maximum number of search results
        """
        self.client = TavilyClient(api_key=api_key)
        self.max_results = max_results
        self._cache: Dict[str, Any] = {}
        logger.info("SearchTool initialized")
    
    def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        topic: Literal["general", "news", "finance"] = "general",
        include_raw_content: bool = False,
    ) -> Dict[str, Any]:
        """Run a web search.
        
        This function performs an internet search using the Tavily API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: uses instance setting)
            topic: Search topic category (general, news, or finance)
            include_raw_content: Whether to include raw HTML content
            
        Returns:
            Dictionary containing search results with keys:
            - query: The search query
            - results: List of search result dictionaries
            - answer: AI-generated answer (if available)
        """
        cache_key = f"{query}:{topic}:{max_results}:{include_raw_content}"
        
        # Check cache
        if cache_key in self._cache:
            logger.info(f"Returning cached results for query: {query}")
            return self._cache[cache_key]
        
        try:
            logger.info(f"Searching for: {query} (topic: {topic})")
            
            results = self.client.search(
                query=query,
                max_results=max_results or self.max_results,
                topic=topic,
                include_raw_content=include_raw_content,
            )
            
            # Cache results
            self._cache[cache_key] = results
            
            logger.info(f"Found {len(results.get('results', []))} results")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                "query": query,
                "results": [],
                "error": str(e),
            }
    
    def clear_cache(self) -> None:
        """Clear the search cache."""
        self._cache.clear()
        logger.info("Search cache cleared")
    
    def get_function_definition(self) -> callable:
        """Get the function definition for use with deepagents.
        
        Returns:
            The search function with proper signature and docstring
        """
        return self.search
