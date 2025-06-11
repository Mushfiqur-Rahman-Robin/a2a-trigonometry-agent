# A2A Trigonometry Assistant

## Description

This project is a multi-agent system based on the `python-a2a` (Agent-to-Agent) protocol. It provides a command-line interface to:
*   Answer various trigonometry questions (calculations, identities, concepts) using the Math Agent.
*   Generate Python code for trigonometric problems using the Coding Agent.
The system leverages an OpenAI model (specifically `gpt-4o-mini` via `ChatOpenAI`) for its intelligent responses.

## Setup

### 1. Python Environment
Ensure you have Python 3.13 or newer installed. (Might work with other versions, no issues)

### 2. Dependencies
It's recommended to use a virtual environment.
The primary dependencies are listed in `pyproject.toml`. You can install them, along with others required by the current implementation, using `uv`:

```bash
uv sync
```
*(Note: `langchain-ollama` is listed but we switched to `langchain-openai`. Use it if you run a test using ollama based LLMs.)*

### 3. Environment Variables
You need to set your OpenAI API key as an environment variable. Create a `.env` file in the project root with the following content:

```
OPENAI_API_KEY="your_openai_api_key_here"
```
The application uses `python-dotenv` (implicitly via `load_dotenv()` in `client.py`) to load this key.

## Running the System

The system consists of three server components that need to be running before the client can be used. Open three separate terminals for the servers:

**1. Start the LLM A2A Server:**
This server provides the interface to the OpenAI LLM.
```bash
PYTHONPATH=./ uv run src/local_llm.py
```
Wait for the message indicating the server has started (e.g., "Starting OpenAI LLM Agent server on port 5001...").

**2. Start the Trigonometry Math Agent:**
```bash
PYTHONPATH=./ uv run src/math_agent/trigonometry_agent.py
```
Wait for its startup message (e.g., "Starting TrigonometryAgent server on port 8001...").

**3. Start the Coding Agent:**
```bash
PYTHONPATH=./ uv run src/coding_agent/code_generator.py
```
Wait for its startup message (e.g., "Starting CodingAgent server on port 8003...").

**4. Run the Client:**
Once all three servers are running, open a new terminal and start the client:
```bash
PYTHONPATH=./ uv run client.py
```

## Usage

The `client.py` application will start in interactive mode. It will first perform health checks on the agents. If they are online, you will see:

```
=== Interactive Mode ===
Enter your trigonometry queries (type 'quit' to exit):

Your query: 
```
Type your trigonometry questions or code requests here. For example:
*   `What is the sine of 30 degrees?`
*   `Write Python code to calculate sine and cosine`
*   `Explain the unit circle`

Type `quit` or `exit` to close the client.
```