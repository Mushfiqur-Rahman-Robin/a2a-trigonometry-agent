import sys
import os
import asyncio
import logging
import json

# Add the 'src' directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from python_a2a import AgentNetwork, A2AClient, AIAgentRouter

# Suppress python_a2a library's internal logging for cleaner output
logging.getLogger("python_a2a").setLevel(logging.WARNING)

# Make query_agent a regular synchronous function
def query_agent(network, llm_client, router, query):
    print(f"\nQuery: {query}")
    
    try:
        # router.route_query is SYNCHRONOUS, so NO 'await' here
        agent_name, confidence = router.route_query(query) 
        print(f"Routing to {agent_name} with {confidence:.2f} confidence")
        
        agent = network.get_agent(agent_name)
        
        # agent.ask is SYNCHRONOUS in this version of python-a2a
        response = agent.ask(query) 
        
        response_text = "No valid response or processing failed."
        
        if isinstance(response, dict):
            result = response.get("result", {})
            status = result.get("status", {})
            
            if status.get("state") == "input-required":
                content_text = status.get("message", {}).get("content", {}).get("text", "Input required message")
                response_text = f"Agent requested input: {content_text}"
            elif "artifacts" in result:
                artifacts = result["artifacts"]
                if artifacts and isinstance(artifacts, list) and len(artifacts) > 0 and "parts" in artifacts[0]:
                    parts = artifacts[0]["parts"]
                    if parts and isinstance(parts, list) and len(parts) > 0 and "text" in parts[0]:
                        response_text = parts[0]["text"]
            else:
                try:
                    response_text = json.dumps(response, indent=2)
                except TypeError:
                    response_text = str(response)
        else:
            response_text = str(response)
            
        print(f"Agent Response: {response_text}")
        
        # Try to get LLM summary, but don't let it crash the whole process
        try:
            # Create a shorter, more focused summary request
            summary_request = f"Briefly summarize this trigonometry result: {response_text[:500]}"
            llm_response = llm_client.ask(summary_request)
            print(f"LLM Summary: {llm_response}")
        except Exception as e:
            print(f"LLM Summary: Error - {str(e)}")
            
    except Exception as e:
        print(f"Error processing query '{query}': {str(e)}")

# Main execution function, now synchronous
def main():
    network = AgentNetwork(name="Trigonometry Assistant Network")
    
    agents = {
        "trigonometry_math": "http://localhost:8001",
        "coding": "http://localhost:8003"
    }
    
    for name, url in agents.items():
        network.add(name, url)
    
    llm_client = A2AClient("http://localhost:5001") 
    
    router = AIAgentRouter(
        llm_client=llm_client, 
        agent_network=network,
        system_prompt="""You are a highly precise routing agent for a trigonometry assistant network. Your task is to route user queries to the most appropriate agent based on their intent:

ROUTING RULES:
1. Route to 'coding' ONLY IF the query explicitly asks for Python code generation:
   - Contains words: 'code', 'python', 'generate code', 'write code', 'script', 'function for', 'program'
   - Examples: 'code for sine calculation', 'python function for angle sum', 'write a script for tangent'

2. Route to 'trigonometry_math' for ALL other trigonometric queries:
   - **Calculations:** 'sine of 30 degrees', 'calculate tan 1.57 radians', 'what is cos(45)?'
   - **Identities/Formulas:** 'list basic identities', 'angle sum formulas', 'show double angle identities'
   - **General questions:** 'what are cofunction formulas?', 'tell me about reciprocal identities'

IMPORTANT: If unsure, default to 'trigonometry_math'. Only use 'coding' when code generation is explicitly requested.

Return your response in the format: agent_name|confidence_score"""
    )
    
    # Test queries
    test_queries = [
        "What is the sine of 30 degrees?",
        "Calculate cos(π/4)",
        "Write Python code to calculate sine and cosine",
        "What are the basic trigonometric identities?",
        "Generate a function for the law of cosines",
        "Explain the unit circle",
        "Code for converting degrees to radians",
        "What is tan(45°)?",
        "Show me the double angle formulas"
    ]
    
    print("=== Trigonometry Assistant Network Client ===")
    print("Testing routing and responses...\n")
    
    # Process each test query
    for query in test_queries:
        query_agent(network, llm_client, router, query)
        print("-" * 60)
    
    # Interactive mode
    print("\n=== Interactive Mode ===")
    print("Enter your trigonometry queries (type 'quit' to exit):")
    
    while True:
        try:
            user_query = input("\nYour query: ").strip()
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_query:
                continue
                
            query_agent(network, llm_client, router, user_query)
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

# Health check function - now synchronous
def check_agents_health(network):
    """Check if all agents are responding"""
    print("Checking agent health...")
    
    for agent_name in network.agents:
        try:
            agent = network.get_agent(agent_name)
            # Simple health check query
            response = agent.ask("ping")
            print(f"✓ {agent_name}: Online")
        except Exception as e:
            print(f"✗ {agent_name}: Offline - {str(e)}")

# Enhanced main with health checks - now synchronous
def main_with_health_check():
    """Main function with agent health verification"""
    network = AgentNetwork(name="Trigonometry Assistant Network")
    
    agents = {
        "trigonometry_math": "http://localhost:8001",
        "coding": "http://localhost:8003"
    }
    
    for name, url in agents.items():
        network.add(name, url)
    
    # Check agent health first
    check_agents_health(network)
    
    # Continue with main execution
    main()

if __name__ == "__main__":
    try:
        # Run the main function directly (no longer async)
        main_with_health_check()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
    except Exception as e:
        print(f"Application error: {e}")
        logging.exception("Detailed error information:")