"""CLI commands using Click framework."""

import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv

from lonai import ResearchAgent
from lonai.cli.formatters import OutputFormatter
from lonai.config import get_settings
from lonai.config.constants import ExportFormat
from lonai.utils.logging import setup_logging
from lonai.utils.validators import validate_api_keys, validate_query

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()

formatter = OutputFormatter()


@click.group()
@click.version_option(version="0.1.0", prog_name="Research Assistant")
def cli() -> None:
    """Research Assistant - AI-powered research tool using DeepAgents.
    
    Conduct thorough research on any topic using advanced AI agents.
    """
    pass


@cli.command()
@click.argument("query", required=False)
@click.option("--lang", "-l", default="en", type=click.Choice(["en", "zh"]), help="Language (en/zh)")
@click.option("--save/--no-save", default=True, help="Save results to storage")
@click.option("--export", "-e", is_flag=True, help="Export formatted report")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["markdown", "html", "json"]),
    default="markdown",
    help="Export format"
)
def research(
    query: Optional[str],
    lang: str,
    save: bool,
    export: bool,
    format: str
) -> None:
    """Conduct research on a topic.
    
    Examples:
    
        research "What is quantum computing?"
        
        research "最新的AI发展趋势" --lang zh
        
        research "Climate change impacts" --export --format html
    """
    # Validate API keys
    valid, error = validate_api_keys()
    if not valid:
        formatter.print_error(error)
        sys.exit(1)
    
    # Get query from user if not provided
    if not query:
        query = formatter.prompt("Enter your research question:")
    
    # Validate query
    valid, error = validate_query(query)
    if not valid:
        formatter.print_error(f"Invalid query: {error}")
        sys.exit(1)
    
    try:
        # Initialize agent
        formatter.print_header("Research Assistant")
        formatter.print_info(f"Query: {query}")
        
        # Auto-detect Chinese if not explicitly set
        if lang == "en" and any('\u4e00' <= char <= '\u9fff' for char in query):
            lang = "zh"
            formatter.print_info("Auto-detected language: zh (Chinese)")
        
        formatter.print_info(f"Language: {lang}")
        
        with formatter.create_progress() as progress:
            task = progress.add_task("Initializing agent...", total=None)
            
            agent = ResearchAgent(language=lang)
            
            progress.update(task, description="Conducting research...")
            
            # Convert export format string to enum
            export_format = ExportFormat(format) if export else None
            
            # Update settings if exporting
            if export:
                agent.settings.export_default_format = export_format
            
            result = agent.research(
                query=query,
                save_results=save,
                export_report=export
            )
            
            progress.update(task, description="Complete!", completed=True)
        
        # Display result
        formatter.print_result(result)
        
    except KeyboardInterrupt:
        formatter.print_warning("\nResearch interrupted by user.")
        sys.exit(130)
    except Exception as e:
        formatter.print_error(f"Research failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--lang", "-l", default="en", type=click.Choice(["en", "zh"]), help="Language")
@click.option("--save/--no-save", default=True, help="Save results")
def batch(file: str, lang: str, save: bool) -> None:
    """Conduct research on multiple topics from a file.
    
    The file should contain one query per line.
    
    Example:
    
        research batch queries.txt
    """
    # Validate API keys
    valid, error = validate_api_keys()
    if not valid:
        formatter.print_error(error)
        sys.exit(1)
    
    # Read queries from file
    try:
        with open(file, 'r', encoding='utf-8') as f:
            queries = [line.strip() for line in f if line.strip()]
    except Exception as e:
        formatter.print_error(f"Failed to read file: {e}")
        sys.exit(1)
    
    if not queries:
        formatter.print_warning("No queries found in file.")
        sys.exit(0)
    
    formatter.print_header("Batch Research")
    formatter.print_info(f"Processing {len(queries)} queries from {file}")
    
    try:
        agent = ResearchAgent(language=lang)
        
        with formatter.create_progress() as progress:
            task = progress.add_task(f"Processing {len(queries)} queries...", total=len(queries))
            
            results = []
            for i, query in enumerate(queries, 1):
                progress.update(task, description=f"[{i}/{len(queries)}] {query[:50]}...")
                
                result = agent.research(query=query, save_results=save, export_report=False)
                results.append(result)
                
                progress.advance(task)
        
        # Summary
        formatter.print_success(f"\nCompleted {len(results)} research tasks.")
        
        # Show brief results
        for i, result in enumerate(results, 1):
            if "error" in result:
                formatter.print_error(f"{i}. {result['query']}: {result['error']}")
            else:
                formatter.print_success(f"{i}. {result['query']}")
        
    except KeyboardInterrupt:
        formatter.print_warning("\nBatch research interrupted by user.")
        sys.exit(130)
    except Exception as e:
        formatter.print_error(f"Batch research failed: {e}")
        sys.exit(1)


@cli.command()
@click.option("--limit", "-n", default=10, help="Number of records to show")
@click.option("--search", "-s", help="Search keyword")
def history(limit: int, search: Optional[str]) -> None:
    """View research history.
    
    Examples:
    
        research history
        
        research history --limit 20
        
        research history --search "quantum"
    """
    try:
        settings = get_settings()
        agent = ResearchAgent(settings=settings)
        
        if search:
            formatter.print_header(f"Search Results: '{search}'")
            records = agent.search_history(search)
        else:
            formatter.print_header("Research History")
            records = agent.get_history(limit=limit)
        
        formatter.print_history(records)
        
    except Exception as e:
        formatter.print_error(f"Failed to retrieve history: {e}")
        sys.exit(1)


@cli.command()
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode")
def chat(interactive: bool) -> None:
    """Interactive chat mode with the research agent.
    
    Example:
    
        research chat --interactive
    """
    # Validate API keys
    valid, error = validate_api_keys()
    if not valid:
        formatter.print_error(error)
        sys.exit(1)
    
    formatter.print_header("Interactive Research Chat")
    formatter.print_info("Type 'exit' or 'quit' to end the session.")
    formatter.print_info("Type 'help' for available commands.")
    
    try:
        agent = ResearchAgent()
        
        while True:
            try:
                query = formatter.prompt("\nYour question")
                
                if not query:
                    continue
                
                if query.lower() in ["exit", "quit", "q"]:
                    formatter.print_success("Goodbye!")
                    break
                
                if query.lower() == "help":
                    formatter.print_info("Commands:")
                    formatter.print_info("  - Type any question to research")
                    formatter.print_info("  - 'exit', 'quit', 'q' to exit")
                    formatter.print_info("  - 'help' to show this message")
                    continue
                
                # Validate query
                valid, error = validate_query(query)
                if not valid:
                    formatter.print_warning(f"Invalid query: {error}")
                    continue
                
                # Conduct research
                with formatter.create_progress() as progress:
                    task = progress.add_task("Researching...", total=None)
                    result = agent.research(query=query, save_results=True, export_report=False)
                    progress.update(task, description="Complete!", completed=True)
                
                # Display response
                formatter.print_markdown(result['response'], title="Research Result")
                
            except KeyboardInterrupt:
                formatter.print_warning("\nUse 'exit' to quit.")
                continue
    
    except Exception as e:
        formatter.print_error(f"Chat session failed: {e}")
        sys.exit(1)


@cli.command()
def config() -> None:
    """Show current configuration.
    
    Display the current application settings.
    """
    try:
        settings = get_settings()
        
        formatter.print_header("Current Configuration")
        
        # Create config display (hide API keys)
        config_data = {
            "Environment": settings.environment,
            "Agent Provider": settings.agent_provider.value,
            "Agent Model": settings.agent_model,
            "Agent Base URL": settings.agent_base_url or "Default",
            "Agent Temperature": settings.agent_temperature,
            "Max Search Results": settings.search_max_results,
            "Default Search Topic": settings.search_default_topic.value,
            "Storage Backend": settings.storage_backend.value,
            "Storage Directory": str(settings.storage_data_dir),
            "Export Format": settings.export_default_format.value,
            "Export Directory": str(settings.export_output_dir),
            "Log Level": settings.log_level,
            "Generic Agent Key": "***" + settings.agent_api_key[-4:] if settings.agent_api_key else "Not set",
            "Anthropic API Key": "***" + settings.anthropic_api_key[-4:] if settings.anthropic_api_key else "Not set",
            "OpenAI API Key": "***" + settings.openai_api_key[-4:] if settings.openai_api_key else "Not set",
            "Google API Key": "***" + settings.google_api_key[-4:] if settings.google_api_key else "Not set",
            "Tavily API Key": "***" + settings.tavily_api_key[-4:] if settings.tavily_api_key else "Not set",
        }
        
        for key, value in config_data.items():
            formatter.print_info(f"{key}: {value}")
        
    except Exception as e:
        formatter.print_error(f"Failed to load configuration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
