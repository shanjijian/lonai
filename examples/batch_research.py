"""Batch research example.

This example demonstrates how to conduct research on multiple topics.
"""

from dotenv import load_dotenv

from lonai import ResearchAgent

# Load environment variables
load_dotenv()

def main():
    """Run batch research on multiple topics."""
    print("=" * 60)
    print("Research Assistant - Batch Research Example")
    print("=" * 60)
    print()
    
    # Define multiple research queries
    queries = [
        "What is artificial intelligence?",
        "Recent advances in renewable energy",
        "Impact of blockchain technology on finance"
    ]
    
    print(f"Processing {len(queries)} research queries:")
    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")
    print()
    
    # Initialize agent
    print("Initializing research agent...")
    agent = ResearchAgent(language="en")
    
    # Conduct batch research
    print("\nConducting batch research...\n")
    results = agent.batch_research(queries=queries, save_results=True)
    
    # Display summary
    print("\n" + "=" * 60)
    print("BATCH RESEARCH SUMMARY")
    print("=" * 60)
    print()
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Query {i}: {result['query']} ---")
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✓ Status: Success")
            if 'saved_path' in result:
                print(f"✓ Saved to: {result['saved_path']}")
            
            # Show first 200 characters of response
            response_preview = result['response'][:200] + "..." if len(result['response']) > 200 else result['response']
            print(f"\nPreview: {response_preview}")
    
    print("\n" + "=" * 60)
    print(f"Completed {len(results)} research tasks.")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBatch research interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
