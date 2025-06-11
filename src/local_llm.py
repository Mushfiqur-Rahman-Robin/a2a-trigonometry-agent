import asyncio
from python_a2a import A2AServer, TaskStatus, TaskState, run_server, skill, agent
from src.utils import parse_task_message
from langchain_openai import ChatOpenAI
import logging
import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@agent(
    name="Custom OpenAI LLM Agent", 
    description="Provides access to an OpenAI LLM using ChatOpenAI, using synchronous methods.",
    version="1.1.0"
)
class CustomLLMAgent(A2AServer):
    def __init__(self, logger=None): 
        super().__init__()
        self.logger = logger if logger else logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers and not logging.getLogger().handlers:
            logging.basicConfig(level=logging.DEBUG) 
            self.logger.warning("Logger was not configured, basicConfig called as fallback in CustomLLMAgent.__init__.")
        
        self.llm = None 
        try:
            self.llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
            self.logger.info(f"Agent '{self.name}' version {self.version} initialized with LLM: {self.llm.model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize ChatOpenAI: {e}. Ensure OPENAI_API_KEY is set.", exc_info=True)

    @skill(
        name="Invoke LLM Sync",
        description="Invokes the ChatOpenAI LLM synchronously with the given query text.",
        examples=["What is the capital of France?", "Summarize this text: ..."]
    )
    def invoke_llm_sync_skill(self, query_text: str) -> str:
        self.logger.debug(f"LLM sync skill received query (first 100 chars): '{query_text[:100]}'")
        
        if not self.llm:
            self.logger.error("ChatOpenAI LLM is not initialized. Cannot process sync skill.")
            return "Error: ChatOpenAI LLM not initialized."

        try:
            self.logger.debug(f"Sending to ChatOpenAI (sync invoke): {query_text[:100]}")
            response_message = self.llm.invoke(query_text) 
            response_str = response_message.content if hasattr(response_message, 'content') else str(response_message)
            
            self.logger.debug(f"ChatOpenAI sync response (first 100 chars): '{response_str[:100]}'")
            return response_str
        except Exception as e:
            self.logger.error(f"Error during ChatOpenAI sync invoke for query '{query_text[:50]}...': {e}", exc_info=True)
            return f"Error invoking ChatOpenAI (sync): {str(e)}"


    def handle_task(self, task):
        self.logger.debug(f"Sync handle_task received by {self.name} (ID: {task.id}): {task.message}")
        query_text = parse_task_message(task)
        
        if not query_text:
            self.logger.warning(f"No query text found in task message for task ID: {task.id}")
            task.status = TaskStatus(
                state=TaskState.ERROR, 
                message={"role": "agent", "content": {"text": "No query text provided in the task message."}}
            )
            return task

        llm_response_text = self.invoke_llm_sync_skill(query_text) 

        if llm_response_text.startswith("Error invoking") or llm_response_text.startswith("Error: ChatOpenAI LLM not initialized.") :
            self.logger.error(f"LLM sync skill returned an error for task ID {task.id}: {llm_response_text}")
            task.status = TaskStatus(
                state=TaskState.ERROR, 
                message={"role": "agent", "content": {"text": llm_response_text}}
            )
        else:
            self.logger.info(f"LLM sync skill successfully processed task ID {task.id}. Response length: {len(llm_response_text)}")
            task.artifacts = [{"parts": [{"type": "text", "text": llm_response_text}]}]
            task.status = TaskStatus(state=TaskState.COMPLETED)
        
        self.logger.debug(f"Sync task ID {task.id} completion status: {task.status.state}, Response snippet: '{llm_response_text[:100]}'")
        return task

def main():
    custom_llm_server = CustomLLMAgent() 
    
    if custom_llm_server.llm is None:
        custom_llm_server.logger.critical("LLM (ChatOpenAI) failed to initialize. Server cannot function. Exiting.")
        return 

    print(f"Starting {custom_llm_server.name} server on port 5001... Press Ctrl+C to stop.")
    run_server(custom_llm_server, port=5001) 

if __name__ == "__main__":
    main()