"""Custom agent example.

This example demonstrates how to create a custom research agent
with custom prompts and configurations.
"""

from dotenv import load_dotenv

from lonai import ResearchAgent, Settings
from lonai.core.prompts import PromptManager
from lonai.config.constants import ExportFormat

# Load environment variables
load_dotenv()

def main():
    """Create and use a custom research agent."""
    print("=" * 60)
    print("Research Assistant - Custom Agent Example")
    print("=" * 60)
    print()
    
    # Create custom settings
    custom_settings = Settings()
    custom_settings.agent_temperature = 0.5  # More focused responses
    custom_settings.search_max_results = 8  # More search results
    custom_settings.export_default_format = ExportFormat.HTML
    
    # Create custom instructions
    custom_instructions = """
    Additional Instructions for this agent:
    
    - Focus on providing practical, actionable insights
    - Include specific examples and case studies when available
    - Highlight recent developments (within the last 6 months)
    - Provide a balanced view with pros and cons
    """
    
    print("Creating custom research agent with:")
    print(f"  - Temperature: {custom_settings.agent_temperature}")
    print(f"  - Max search results: {custom_settings.search_max_results}")
    print(f"  - Custom focused instructions")
    print()
    
    # Initialize agent with custom settings
    agent = ResearchAgent(
        settings=custom_settings,
        language="en",
        custom_instructions=custom_instructions
    )
    
    # Research query
    query = "What are the practical applications of machine learning in healthcare?"
    print(f"Query: {query}")
    print("\nConducting research with custom agent...\n")
    
    # Conduct research with export
    result = agent.research(
        query=query,
        save_results=True,
        export_report=True
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("CUSTOM AGENT RESEARCH RESULTS")
    print("=" * 60)
    print()
    print(result['response'])
    print()
    
    if 'saved_path' in result:
        print(f"✓ Results saved to: {result['saved_path']}")
    
    if 'report_path' in result:
        print(f"✓ HTML report exported to: {result['report_path']}")
    
    print()
    print("=" * 60)
    print("\nTip: You can customize the agent with:")
    print("  - Different temperature settings for response style")
    print("  - Custom system prompts for specialized behavior")
    print("  - Different search parameters for broader/narrower results")
    print("  - Export formats (Markdown, HTML, JSON)")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nResearch interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
