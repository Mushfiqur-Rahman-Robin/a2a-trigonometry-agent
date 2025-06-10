# src/local_llm.py (or just local_llm.py if it's in root)

from python_a2a import A2AClient, run_server
from python_a2a.langchain import to_a2a_server
from langchain_ollama.llms import OllamaLLM
import threading
import signal
import sys

def main():
    llm = OllamaLLM(model="llama3.2:1b", 
                    system_prompt="You are a precise trigonometry assistant that can perform calculations, provide identities, and generate Python code. You will be used by a routing agent to decide which specific tool to use based on the user's query.") # Clarified prompt
    llm_server = to_a2a_server(llm)
    llm_thread = threading.Thread(
        target=lambda: run_server(llm_server, port=5001),
        daemon=True
    )
    llm_thread.start()
    try:
        print("LLM server running on port 5001. Press Ctrl+C to stop.")
        signal.pause()
    except KeyboardInterrupt:
        print("\nStopping LLM server...")
        sys.exit(0)

if __name__ == "__main__":
    main()