from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState, A2AClient
from src.utils import setup_logging, parse_task_message
import logging 
import httpx

@agent(
    name="Trigonometry Agent",
    description="Provides expert answers to trigonometric queries. It can perform calculations (e.g., 'sine of 30 degrees'), list identities (e.g., 'show me angle sum formulas'), or explain trigonometric concepts. This agent uses an LLM for its responses and does not generate code.",
    version="1.1.0"
)
class TrigonometryAgent(A2AServer):
    def __init__(self):
        super().__init__()
        self.logger = setup_logging(self.__class__.__name__)
        try:
            self.llm_client = A2AClient("http://localhost:5001")
            self.logger.info("A2AClient for LLM initialized successfully in TrigonometryAgent.")
        except Exception as e:
            self.logger.error(f"Failed to initialize A2AClient for LLM in TrigonometryAgent: {e}", exc_info=True)
            self.llm_client = None

    @skill(
        name="Get Trigonometric Response",
        description="Answers trigonometric queries. Performs calculations (e.g., 'sine of 30 degrees'), provides identities (e.g., 'list angle sum formulas'), or explains concepts (e.g., 'what is the unit circle?').",
        tags=["trigonometry", "calculation", "identity", "formula", "sine", "cosine", "tangent", "math", "expert", "concept", "explanation"],
        examples=[
            "Calculate cos(π/4)", 
            "What are the Pythagorean identities?", 
            "Explain the law of sines", 
            "value of tan(60 degrees)",
            "list all double angle formulas"
        ]
    )
    def get_trigonometric_response(self, query_text: str) -> str:
        """Answers trigonometric queries using an LLM via raw httpx (synchronous)."""
        self.logger.debug(f"Processing trigonometric query for LLM (sync httpx): '{query_text}'")

        prompt_text_for_llm = (
            "You are a trigonometry expert. Answer the following trigonometric query: "
            f"'{query_text}'. "
            "If it's a calculation, provide the numerical result, showing steps if complex. "
            "If it's a request for identities, list them clearly and concisely. "
            "If it's a conceptual question, explain it accurately. "
            "Avoid conversational fluff and stick to the facts. Format identities or lists clearly."
            "Do not answer anything except trigonometry even if user persists."
        )
        
        llm_server_url = "http://localhost:5001/tasks/send"
        payload = {"message": {"content": {"text": prompt_text_for_llm}}}

        try:
            raw_response = httpx.post(llm_server_url, json=payload, timeout=30.0) # Direct blocking call, increased timeout

            if raw_response.status_code == 200:
                response_json = raw_response.json()
                try:
                    # CustomLLMAgent returns artifacts directly at the top level of the JSON body
                    generated_text = response_json["artifacts"][0]["parts"][0]["text"]
                    return generated_text.strip()
                except (KeyError, IndexError, TypeError) as e:
                    self.logger.error(f"Error parsing LLM JSON response: {e} - JSON: {response_json}", exc_info=True)
                    return f"Error: Could not parse LLM response: {str(response_json)}"
            else:
                self.logger.error(f"LLM server error: Status {raw_response.status_code} - {raw_response.text[:200]}")
                return f"Error: LLM server returned status {raw_response.status_code}"
        except httpx.TimeoutException as e: # More specific exception
            self.logger.error(f"Timeout during httpx call to LLM: {e}", exc_info=True)
            return f"Error: Timeout communicating with LLM: {str(e)}"
        except Exception as e:
            self.logger.error(f"Error during httpx call to LLM: {e}", exc_info=True)
            return f"Error: Could not communicate with LLM: {str(e)}"

    def handle_task(self, task):
        text = parse_task_message(task)
        self.logger.info(f"TrigonometryAgent received task (sync handle_task): '{text}'")

        if not self.llm_client:
            self.logger.error("LLM client not available in handle_task of TrigonometryAgent.")
            task.status = TaskStatus(
                state=TaskState.FAILED,
                message={"role": "agent", "content": {"text": "LLM client is not initialized. Cannot process trigonometry task."}}
            )
            return task
            
        # Reject code generation requests explicitly, though router should prevent this
        if any(k in text.lower() for k in ["code", "python", "generate", "script", "program"]):
             self.logger.warning(f"TrigonometryAgent received a query that seems to ask for code: '{text}'. This agent does not generate code.")
             task.status = TaskStatus(
                state=TaskState.FAILED,
                message={"role": "agent", "content": {"text": "This agent provides trigonometric calculations and identity information, not code. Please route coding requests to the 'coding' agent."}}
            )
             return task

        try:
            result = self.get_trigonometric_response(text)
            
            if result is None or "Error:" in result:
                self.logger.error(f"Trigonometric response generation failed or returned an error for query '{text}': {result}")
                task.status = TaskStatus(
                    state=TaskState.FAILED,
                    message={"role": "agent", "content": {"text": result or "Trigonometric response generation failed."}}
                )
            else:
                self.logger.info(f"Successfully generated trigonometric response for query: '{text}'")
                task.artifacts = [{"parts": [{"type": "text", "text": result}]}]
                task.status = TaskStatus(state=TaskState.COMPLETED)
                
        except Exception as e:
            self.logger.error(f"Error in TrigonometryAgent handle_task for query '{text}': {e}", exc_info=True)
            task.status = TaskStatus(
                state=TaskState.FAILED,
                message={"role": "agent", "content": {"text": f"An unexpected error occurred in TrigonometryAgent handle_task: {str(e)}"}}
            )
        
        return task

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG) 
    agent = TrigonometryAgent()
    agent.logger.info("Starting TrigonometryAgent server on port 8001...") 
    run_server(agent, port=8001, debug=True)