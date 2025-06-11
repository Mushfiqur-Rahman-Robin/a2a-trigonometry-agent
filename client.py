import sys
import os
import asyncio
import logging
import json
import httpx

# Add the 'src' directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from python_a2a import AgentNetwork, A2AClient, AIAgentRouter

# Suppress python_a2a library's internal logging for cleaner output
logging.getLogger("python_a2a").setLevel(logging.WARNING)

async def query_agent(network, llm_client, router, query):
    loop = asyncio.get_event_loop()
    print(f"\nQuery: {query}")
    
    try:
        # router.route_query is a blocking call (we offload it to a separate thread to avoid blocking the async flow.)
        agent_name, confidence = await loop.run_in_executor(None, router.route_query, query)
        print(f"Routing to {agent_name} with {confidence:.2f} confidence")
        
        agent = network.get_agent(agent_name)
        
        # agent.ask is a blocking call (we offload it to a separate thread to avoid blocking the async flow.)
        response = await loop.run_in_executor(None, agent.ask, query)
        
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
        
        try:
            print("DEBUG: Attempting raw httpx.post to LLM server for summary/ping.")
            llm_server_url = "http://localhost:5001/tasks/send" 
            ping_payload = {"message": {"content": {"text": "Hello LLM, this is a client ping."}}}

            # Comment out the A2AClient based summary call
            # summary_request = f"Briefly summarize this trigonometry result: {response_text[:500]}"
            # temp_summary_llm_client = A2AClient("http://localhost:5001")
            # # print("DEBUG: Created temporary LLM client for summary.")
            # llm_response = await loop.run_in_executor(None, temp_summary_llm_client.ask, summary_request)
            # print(f"LLM Summary: {llm_response}")

            http_post_lambda = lambda: httpx.post(llm_server_url, json=ping_payload, timeout=10)
            raw_response = await loop.run_in_executor(None, http_post_lambda)
            
            print(f"DEBUG: LLM raw status: {raw_response.status_code}")
            # print(f"DEBUG: LLM raw response: {raw_response.text[:200]}") 
            
            if raw_response.status_code == 200:
                response_json = raw_response.json()
                llm_summary_text = "Could not extract text from raw response."

                # Attempt to extract text, structure depends on A2AServer response
                if response_json.get("result", {}).get("artifacts") and \
                   len(response_json["result"]["artifacts"]) > 0 and \
                   response_json["result"]["artifacts"][0].get("parts") and \
                   len(response_json["result"]["artifacts"][0]["parts"]) > 0 and \
                   "text" in response_json["result"]["artifacts"][0]["parts"][0]:
                    llm_summary_text = response_json["result"]["artifacts"][0]["parts"][0]["text"]
                elif response_json.get("message", {}).get("content", {}).get("text"): # Fallback for simple text responses
                    llm_summary_text = response_json["message"]["content"]["text"]
                print(f"LLM Ping/Summary (raw httpx): {llm_summary_text}")
            else:
                print(f"LLM Ping/Summary (raw httpx) Error: Status {raw_response.status_code} - {raw_response.text[:200]}")

        except Exception as e:
            print(f"LLM Summary (raw httpx): Error - {str(e)}")
            
    except Exception as e:
        print(f"Error processing query '{query}': {str(e)}")

async def main():
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
        system_prompt="You are an agent routing system. Based on the user's query, decide which agent is best suited to handle it. \
            The available agents are 'trigonometry_math' for calculations and trigonometric identities, and 'coding' for generating Python code. \
            Return your response in the format: agent_name|confidence_score. For confidence_score, use 1.0 if you are confident, or 0.5 if you are unsure. Example: 'coding|1.0'."
    )
    
    # Test queries
    # test_queries = [
    #     "What is the sine of 30 degrees?",
    #     "Calculate cos(π/4)",
    #     "Write Python code to calculate sine and cosine",
    #     "What are the basic trigonometric identities?",
    #     "Generate a function for the law of cosines",
    #     "Explain the unit circle",
    #     "Code for converting degrees to radians",
    #     "What is tan(45°)?",
    #     "Show me the double angle formulas"
    # ]
    
    print("=== Trigonometry Assistant Network Client ===")
    # print("Testing routing and responses...\n")
    
    # # Process each test query
    # for query in test_queries:
    #     await query_agent(network, llm_client, router, query) # Ensure correct parameters
    #     print("-" * 60)
    
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
            
            # Ensure there's a query before running    
            await query_agent(network, llm_client, router, user_query)
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

async def check_agents_health(network):
    """Check if all agents are responding"""
    loop = asyncio.get_event_loop()
    print("Checking agent health...")
    
    for agent_name in network.agents:
        try:
            agent = network.get_agent(agent_name)
            # Simple health check query - agent.ask is blocking
            response = await loop.run_in_executor(None, agent.ask, "ping")
            print(f"✓ {agent_name}: Online")
        except Exception as e:
            print(f"✗ {agent_name}: Offline - {str(e)}")

async def main_with_health_check():
    """Main function with agent health verification"""
    network = AgentNetwork(name="Trigonometry Assistant Network")
    
    agents = {
        "trigonometry_math": "http://localhost:8001",
        "coding": "http://localhost:8003"
    }
    
    for name, url in agents.items():
        network.add(name, url)
    
    await check_agents_health(network)
    
    # Continue with main execution
    await main()

if __name__ == "__main__":
    try:
        asyncio.run(main_with_health_check())
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
    except Exception as e:
        print(f"Application error: {e}")
        logging.exception("Detailed error information:")