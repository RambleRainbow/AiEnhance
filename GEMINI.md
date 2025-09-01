# Gemini Project Context: AiEnhance

## Project Overview

This project, **AiEnhance**, is a sophisticated AI cognitive enhancement system built with Python. Its core purpose is to create a "memory-cognitive collaboration system" that goes beyond traditional Retrieval-Augmented Generation (RAG). It aims to build an intelligent system with capabilities for memory filtering and reconstruction, semantic association, and cognitive amplification.

The system is built on a four-layer architecture:
1.  **Perception Layer:** Handles user modeling and context analysis.
2.  **Cognition Layer:** Manages memory activation, semantic enhancement, and analogy-based reasoning.
3.  **Behavior Layer:** Produces adaptive output tailored to the user and context.
4.  **Collaboration Layer:** Facilitates human-AI cognitive collaboration through features like dialectical perspectives and cognitive challenges.

## Key Technologies

*   **Programming Language:** Python 3.12.9
*   **Package Management:** `uv`
*   **Code Quality:** `ruff` for linting and formatting.
*   **Core Framework:** The project uses a custom-built layered architecture.
*   **LLM Integration:** Flexible support for multiple LLM providers, including local models via `Ollama` (recommended), `OpenAI`, and `Anthropic`.
*   **Memory Systems:** Pluggable architecture for different memory backends like `Graphiti` (a graph-based system using Neo4j), and `Mem0`.
*   **User Interface:** Provides both a command-line interface (`cli_example.py`) and a web-based UI using `Gradio` (`gradio_interface.py`).
*   **Containerization:** `Docker` and `Docker Compose` are available for setting up dependent services like `Graphiti` and `PostgreSQL`.

## Building and Running

### 1. Environment Setup

The project uses `uv` for managing Python dependencies.

```bash
# Clone the repository
git clone https://github.com/your-username/AiEnhance.git
cd AiEnhance

# Install dependencies using uv
uv sync
```

### 2. Local LLM Setup (Ollama)

The system is designed to work well with local LLMs via Ollama. A setup script is provided.

```bash
# Make sure the Ollama service is running in a separate terminal
# ollama serve

# Run the setup script to download the recommended models
./scripts/setup-ollama.sh
```
The script will download the recommended models: `qwen3:8b` (for generation) and `bge-m3` (for embeddings).

### 3. Running the Application

The application can be run in two modes:

**CLI Mode (with streaming output):**
```bash
# Run with a single query
uv run python cli_example.py "What is artificial intelligence?"

# Run in interactive chat mode
uv run python cli_example.py -i
```

**Gradio Web Interface:**
```bash
# Start the Gradio server
uv run python gradio_interface.py
```
The web interface will be available at `http://localhost:7860`.

### 4. Running with Docker (for dependent services)

If you plan to use the `Graphiti` memory system, you'll need to run its backing services (Neo4j, etc.) via Docker.

```bash
# Start the dependent services (Graphiti, PostgreSQL)
docker-compose -f docker/docker-compose.deps.yml up -d

# To start the full application stack with Docker:
# ./docker-start.sh
```

## Development Conventions

### Code Style

The project uses `ruff` to enforce a consistent code style.
*   **Line Length:** 88 characters
*   **Quote Style:** Double quotes (`"`)
*   **Indent Style:** Spaces

Use the following commands to maintain code quality:
```bash
# Check for linting errors
uv run ruff check .

# Format the code
uv run ruff format .
```

### Testing

The project uses `pytest` for testing. Tests are located in the `tests/` directory.

```bash
# Run all tests
uv run python -m pytest tests/
```

### Configuration

Configuration is managed via environment variables and centralized in `aienhance/config.py`. A `.env.example` file is provided as a template. Key configurations include:
*   `DEFAULT_LLM_PROVIDER` (e.g., `ollama`, `openai`)
*   `DEFAULT_LLM_MODEL`
*   `DEFAULT_MEMORY_SYSTEM` (e.g., `graphiti_http`)
*   `OLLAMA_BASE_URL`
*   `GRAPHITI_API_URL`

The system's behavior, such as enabling/disabling the memory system or the collaboration layer, can be controlled through these environment variables.
