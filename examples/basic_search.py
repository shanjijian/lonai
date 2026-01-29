"""Basic search example using the Research Assistant.

This example demonstrates how to use the ResearchAgent for simple searches.
"""

import os
from dotenv import load_dotenv

from lonai import ResearchAgent
from lonai.config import get_settings

# Load environment variables from .env file
load_dotenv()

def main():
    """Run a basic search example."""
    print("=" * 60)
    print("Research Assistant - Basic Search Example")
    print("=" * 60)
    print()
    
    # Initialize the research agent
    print("Initializing research agent...")
    agent = ResearchAgent(language="en")
    
    # Define research query
    query = "What are the latest developments in quantum computing?"
    print(f"\nQuery: {query}")
    print("\nConducting research...\n")
    
    # Conduct research
    result = agent.research(
        query=query,
        save_results=True,
        export_report=False
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("RESEARCH RESULTS")
    print("=" * 60)
    print()
    print(result['response'])
    print()
    
    if 'saved_path' in result:
        print(f"✓ Results saved to: {result['saved_path']}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nResearch interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
