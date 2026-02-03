"""Core research agent implementation using DeepAgents."""

import logging
import os
from typing import Any, Dict, List, Optional

from deepagents import create_deep_agent

from lonai.config.settings import Settings, get_settings
from lonai.core.prompts import PromptManager
from lonai.tools.search import SearchTool
from lonai.tools.storage import StorageManager
from lonai.tools.export import ReportExporter

logger = logging.getLogger(__name__)


class ResearchAgent:
    """Enterprise-grade research agent powered by DeepAgents.
    
    This class encapsulates the creation and configuration of a deep agent
    for conducting research tasks.
    """
    
    def __init__(
        self,
        settings: Optional[Settings] = None,
        language: str = "en",
        custom_instructions: Optional[str] = None
    ):
        """Initialize the research agent.
        
        Args:
            settings: Application settings (uses defaults if not provided)
            language: Language for prompts ("en" or "zh")
            custom_instructions: Optional custom instructions to append to system prompt
        """
        self.settings = settings or get_settings()
        self.language = language
        self.prompt_manager = PromptManager(language=language)
        
        # Initialize tools
        self.search_tool = SearchTool(
            api_key=self.settings.tavily_api_key,
            max_results=self.settings.search_max_results
        )
        
        self.storage_manager = StorageManager(
            data_dir=self.settings.storage_data_dir,
            auto_save=self.settings.storage_auto_save
        )
        
        self.report_exporter = ReportExporter(
            output_dir=self.settings.export_output_dir
        )
        
        # Configure Model
        model = self._configure_model()
        
        # Create agent
        system_prompt = self.prompt_manager.get_research_prompt(custom_instructions)
        
        # Get skills directory if configured
        # FilesystemBackend uses relative paths (no leading slash)
        # Other backends like StateBackend use POSIX paths ("/skills/")
        skills_dirs = ["skills"] if self.settings.skills_dir and self.settings.skills_dir.exists() else []
        
        # Configure Backend with execution support
        from lonai.core.backend import LocalExecutionBackend
        from pathlib import Path
        
        # Use project root as the filesystem root
        project_root = Path(__file__).parent.parent.parent.parent
        
        self.agent = create_deep_agent(
            model=model,
            tools=[self.search_tool.get_function_definition()],
            system_prompt=system_prompt,
            skills=skills_dirs,
            backend=LocalExecutionBackend(root_dir=str(project_root)),
            debug=False,  # Enable debug logging
        )
        
        logger.info(f"ResearchAgent initialized with provider: {self.settings.agent_provider}, skills_dir: {skills_dirs}")



    def _configure_model(self) -> Any:
        """Configure the LLM based on settings."""
        from lonai.config.constants import AgentProvider
        
        provider = self.settings.agent_provider
        
        # Resolve API Key
        api_key = self.settings.agent_api_key
        if not api_key:
            if provider == AgentProvider.ANTHROPIC:
                api_key = self.settings.anthropic_api_key
            elif provider == AgentProvider.OPENAI:
                api_key = self.settings.openai_api_key
            elif provider == AgentProvider.GOOGLE:
                api_key = self.settings.google_api_key
        
        if not api_key and provider != AgentProvider.CUSTOM:
             # Logic is handled by pydantic validator mostly, but double check here
             pass

        if provider == AgentProvider.ANTHROPIC:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=self.settings.agent_model,
                api_key=api_key,
                temperature=self.settings.agent_temperature,
                max_tokens=self.settings.agent_max_tokens,
            )
            
        elif provider == AgentProvider.OPENAI or provider == AgentProvider.CUSTOM:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=self.settings.agent_model,
                api_key=api_key or "dummy", # Custom/Local use cases might not strictly need key
                base_url=self.settings.agent_base_url,
                temperature=self.settings.agent_temperature,
                max_tokens=self.settings.agent_max_tokens,
            )
            
        elif provider == AgentProvider.GOOGLE:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=self.settings.agent_model,
                google_api_key=api_key,
                temperature=self.settings.agent_temperature,
                max_output_tokens=self.settings.agent_max_tokens,
            )
            
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def research(
        self,
        query: str,
        save_results: bool = True,
        export_report: bool = False
    ) -> Dict[str, Any]:
        """Conduct research on a given query.
        
        Args:
            query: Research question or topic
            save_results: Whether to save results to storage
            export_report: Whether to export a formatted report
            
        Returns:
            Dictionary containing:
            - query: The research query
            - response: Agent's response
            - saved_path: Path to saved results (if save_results=True)
            - report_path: Path to exported report (if export_report=True)
        """
        logger.info(f"Starting research: {query}")
        
        try:
            # Invoke the agent
            result = self.agent.invoke({
                "messages": [{"role": "user", "content": query}]
            })
            
            # DEBUG: Dump full result to file for analysis
            try:
                import json
                DEBUG_FILE = os.path.join(self.settings.storage_data_dir, "debug_last_result.txt")
                with open(DEBUG_FILE, "w", encoding="utf-8") as f:
                    f.write(f"Query: {query}\n\n")
                    f.write(f"Result Keys: {list(result.keys())}\n\n")
                    f.write("Messages:\n")
                    for i, msg in enumerate(result["messages"]):
                        f.write(f"--- Message {i} ---\n")
                        f.write(f"Type: {type(msg)}\n")
                        f.write(f"Content: {repr(msg.content)}\n")
                        f.write(f"Additional Kwargs: {msg.additional_kwargs}\n")
                        if hasattr(msg, "tool_calls"):
                            f.write(f"Tool Calls: {msg.tool_calls}\n")
                        f.write("\n")
                logger.info(f"Debug info saved to {DEBUG_FILE}")
            except Exception as e:
                logger.error(f"Failed to write debug log: {e}")
            
            # Extract response
            # Robust extraction: find the last AI message with actual content.
            # This handles cases where the final message might be empty (e.g. due to model quirks or tool artifacts).
            response = ""
            messages = result["messages"]
            for msg in reversed(messages):
                if msg.type == "ai":
                    if msg.content:
                        response = msg.content
                        break
                    # Fallback for DeepSeek/Reasoning models
                    if msg.additional_kwargs.get("reasoning_content"):
                        response = msg.additional_kwargs.get("reasoning_content")
                        break
            
            # Fallback to the last message content if no valid AI message found
            if not response and messages:
                response = messages[-1].content
            
            output = {
                "query": query,
                "response": response,
            }
            
            # Save results if requested
            if save_results:
                saved_path = self.storage_manager.save_research(
                    query=query,
                    results=response,
                    metadata={"language": self.language}
                )
                output["saved_path"] = str(saved_path)
            
            # Export report if requested
            if export_report:
                report_path = self.report_exporter.export(
                    content=response,
                    title=query,
                    format=self.settings.export_default_format,
                    metadata={"query": query, "language": self.language}
                )
                output["report_path"] = str(report_path)
            
            logger.info("Research completed successfully")
            return output
            
        except Exception as e:
            logger.error(f"Research error: {e}")
            raise
    
    def batch_research(
        self,
        queries: List[str],
        save_results: bool = True
    ) -> List[Dict[str, Any]]:
        """Conduct research on multiple queries.
        
        Args:
            queries: List of research questions
            save_results: Whether to save results
            
        Returns:
            List of result dictionaries
        """
        logger.info(f"Starting batch research: {len(queries)} queries")
        
        results = []
        for i, query in enumerate(queries, 1):
            logger.info(f"Processing query {i}/{len(queries)}: {query}")
            try:
                result = self.research(
                    query=query,
                    save_results=save_results,
                    export_report=False
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing query '{query}': {e}")
                results.append({
                    "query": query,
                    "error": str(e)
                })
        
        logger.info("Batch research completed")
        return results
    
    def get_history(self, limit: Optional[int] = 10) -> List[Dict[str, Any]]:
        """Get research history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of research history metadata
        """
        return self.storage_manager.list_research(limit=limit)
    
    def search_history(self, keyword: str) -> List[Dict[str, Any]]:
        """Search research history by keyword.
        
        Args:
            keyword: Search keyword
            
        Returns:
            List of matching research records
        """
        return self.storage_manager.search_research(keyword)
