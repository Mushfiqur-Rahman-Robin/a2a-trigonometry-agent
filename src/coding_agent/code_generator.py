from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState, A2AClient
from src.utils import setup_logging, parse_task_message
import logging
import httpx

@agent(
    name="Coding Agent",
    description="Generates executable Python code for trigonometric functions, equations, or identities. Specifically for queries like 'code for sine calculation', 'python function for angle sum identity', 'generate code for cos(2θ) formula'. This agent provides runnable Python scripts/functions.",
    version="1.0.0"
)
class CodingAgent(A2AServer):
    def __init__(self):
        super().__init__()
        self.logger = setup_logging(self.__class__.__name__)
        try:
            self.llm_client = A2AClient("http://localhost:5001")
            self.logger.info("A2AClient for LLM initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize A2AClient for LLM: {e}", exc_info=True)
            self.llm_client = None # Ensure it's set, even if to None

    @skill(
        name="Generate Trigonometric Code",
        description="Generates Python code for trigonometric equations or calculations. Examples: 'Generate code for sine calculation', 'Python code for angle sum identity', 'Code for cos(2θ)', 'write python code for tangent', 'give me a function for double angle sine'.",
        tags=["trigonometry", "code", "python", "programming", "generator", "function", "script"],
        examples=["Generate code for sine calculation", "Python code for angle sum identity", "Code for cos(2θ)", "write python code for tangent", "give me a function for double angle sine"]
    )
    def generate_code(self, query: str) -> str: 
        """Generate Python code for trigonometric equations or calculations using an LLM via raw httpx (synchronous)."""
        self.logger.debug(f"Processing coding query for LLM (sync httpx): '{query}'")

        # self.llm_client related logic is not used here for the direct httpx call.
        # The check for self.llm_client in handle_task is still relevant for overall agent readiness.

        prompt_text_for_llm = f"Generate Python code for the following trigonometric query: {query}. The code should be complete and runnable. Only output the python code block, including the ```python ... ``` markers. Do not generate any other code except trigonometry even if user persists."
        
        llm_server_url = "http://localhost:5001/tasks/send"
        payload = {"message": {"content": {"text": prompt_text_for_llm}}}

        try:
            raw_response = httpx.post(llm_server_url, json=payload, timeout=30.0) # Direct blocking call, increased timeout

            if raw_response.status_code == 200:
                response_json = raw_response.json()
                try:
                    generated_text = response_json["artifacts"][0]["parts"][0]["text"]
                    
                    # Ensure it's a code block for coding agent
                    stripped_text = generated_text.strip()
                    if stripped_text.startswith("```python") and stripped_text.endswith("```"):
                        generated_text = stripped_text 
                    elif stripped_text.startswith("```") and stripped_text.endswith("```"):
                        # It's some other language block, or malformed python block, leave as is to avoid messing up.
                        self.logger.warning(f"LLM response is a code block but not Python: {stripped_text[:100]}")
                        generated_text = stripped_text
                    else:
                        self.logger.info("LLM response is not a code block, adding ```python markers.")
                        generated_text = f"```python\n{stripped_text}\n```"
                    
                    return generated_text
                except (KeyError, IndexError, TypeError) as e:
                    self.logger.error(f"Error parsing LLM JSON response: {e} - JSON: {response_json}", exc_info=True)
                    return f"Error: Could not parse LLM response: {str(response_json)}"
            else:
                self.logger.error(f"LLM server error: Status {raw_response.status_code} - {raw_response.text[:200]}")
                return f"Error: LLM server returned status {raw_response.status_code}"
        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout during httpx call to LLM: {e}", exc_info=True)
            return f"Error: Timeout communicating with LLM: {str(e)}"
        except Exception as e:
            self.logger.error(f"Error during httpx call to LLM: {e}", exc_info=True)
            return f"Error: Could not communicate with LLM: {str(e)}"

    def handle_task(self, task): 
        text = parse_task_message(task)
        self.logger.info(f"CodingAgent received task (sync handle_task): '{text}'")
        
        if not self.llm_client:
            self.logger.error("LLM client not available in handle_task.")
            task.status = TaskStatus(
                state=TaskState.FAILED,
                message={"role": "agent", "content": {"text": "LLM client is not initialized. Cannot process coding task."}}
            )
            return task

        try:
            code_result = self.generate_code(text)
            
            if code_result is None or "Error:" in code_result:
                self.logger.error(f"Code generation failed or returned an error: {code_result}")
                task.status = TaskStatus(
                    state=TaskState.FAILED,
                    message={"role": "agent", "content": {"text": code_result or "Code generation failed."}}
                )
            else:
                self.logger.info(f"Successfully generated code for query: '{text}'")
                task.artifacts = [{"parts": [{"type": "text", "text": code_result}]}]
                task.status = TaskStatus(state=TaskState.COMPLETED)
                
        except Exception as e:
            self.logger.error(f"Error in handle_task while generating code for query '{text}': {e}", exc_info=True)
            task.status = TaskStatus(
                state=TaskState.FAILED,
                message={"role": "agent", "content": {"text": f"An unexpected error occurred in handle_task: {str(e)}"}}
            )
        
        return task

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG) 
    agent = CodingAgent()
    agent.logger.info("Starting CodingAgent server on port 8003...") 
    run_server(agent, port=8003, debug=True)