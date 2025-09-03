# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Package Management (UV Recommended)
```bash
# Install dependencies
uv sync

# Activate virtual environment (automatic when using uv run)
# Manual activation: source .venv/bin/activate
```

### Environment Configuration
```bash
# Copy environment template (first time setup)
cp .env.example .env

# Check current configuration
uv run python scripts/check_config.py

# All configurations can be customized via environment variables in .env file
```

### Running the Application
```bash
# Command-line interface (默认流式输出)
uv run python cli_example.py "your question here"
uv run python cli_example.py -i  # Interactive mode with streaming

# Web interface (Gradio) - 支持流式输出选择
uv run python gradio_interface.py
# Access at http://localhost:7860
```

### Code Quality & Linting
Run ruff to lint codes BEFORE commit
```bash
# Code checking
uv run ruff check .

# Code formatting
uv run ruff format .
```

### Testing
```bash
# Run all tests
uv run python -m pytest tests/

# Run specific test file
uv run python -m pytest tests/test_system_architecture.py

# Run specific test function
uv run python -m pytest tests/test_system_architecture.py::test_system_creation
```

### Ollama Setup (Required for Local LLM)
```bash
# Install Ollama models using provided script
./scripts/setup-ollama.sh

# Manual Ollama setup
ollama serve  # Start Ollama service
ollama pull qwen3:8b  # Main model
ollama pull bge-m3:latest  # Embedding model
```

### Graphiti Memory System Setup (Required for Memory Features)
```bash
# Navigate to your Graphiti project directory
cd /Users/hongling/Dev/claude/graphiti

# Start Graphiti services (Neo4j + Graphiti API)
docker-compose up -d

# Verify services are running
curl http://localhost:8000/healthcheck  # Should return HTTP 200
```

**Graphiti Service Details:**
- **API Service**: http://localhost:8000 (Graphiti REST API)
- **Neo4j Database**: bolt://localhost:7687 (Graph database)
- **Neo4j Browser**: http://localhost:7474 (Database management UI)

**Default Credentials:**
- Neo4j Username: `neo4j`
- Neo4j Password: `neo4j_passwd`

## Architecture Overview

This is a **Layered Cognitive System** that implements memory-cognitive synergy beyond traditional RAG approaches.

### Core Architecture: 4-Layer Design

1. **Perception Layer** (`aienhance/perception/`)
   - User modeling and profiling (`user_modeling.py`)
   - Context analysis and situation understanding (`context_analysis.py`)
   - Entry point for all user input processing

2. **Cognition Layer** (`aienhance/cognition/`)
   - Memory activation and retrieval (`memory_activation.py`)
   - Semantic enhancement of retrieved information (`semantic_enhancement.py`)
   - Analogy reasoning and pattern matching (`analogy_reasoning.py`)

3. **Behavior Layer** (`aienhance/behavior/`)
   - Adaptive content output based on user profile (`adaptive_output.py`)
   - LLM-driven response generation with personalization
   - Content optimization and quality metrics

4. **Collaboration Layer** (`aienhance/collaboration/`)
   - Multi-perspective generation (`dialectical_perspective.py`)
   - Cognitive challenge creation (`cognitive_challenge.py`)
   - Collaborative reasoning coordination (`collaborative_coordinator.py`)

### System Factories and Initialization

**Primary Entry Points:**
- `enhanced_system_factory.py`: Main factory for creating systems
- `create_layered_system()`: **Recommended** - Creates new layered architecture

**System Types:**
- `educational`: Optimized for learning scenarios
- `research`: Enhanced analytical capabilities
- `creative`: Higher temperature, creative thinking
- `lightweight`: Minimal resource usage, no collaboration layer

### Memory System Integration

**Graphiti Integration** (Default):
- `graphiti_adapter.py`: Neo4j-based temporal knowledge graph memory system
- Supports both HTTP API and native client modes
- Automatic temporal relationship tracking and hybrid search capabilities
- External Docker service architecture for better resource isolation

**Alternative Memory Systems:**
- `mem0_adapter.py`: Mem0 integration (lightweight alternative)

### LLM Provider Support

**Supported Providers** (`aienhance/llm/adapters/`):
- `ollama_adapter.py`: Local Ollama (recommended for development)
- `openai_adapter.py`: OpenAI API
- `anthropic_adapter.py`: Anthropic Claude

**Default Configuration:**
- Provider: Ollama
- Model: qwen3:8b
- Embedding: bge-m3:latest
- Base URL: http://localhost:11434

## Important Implementation Details

### Information Flow Architecture
```
User Input → Perception Layer → Cognition Layer → Behavior Layer → Collaboration Layer → Final Response
```

Each layer produces structured output objects that serve as input to the next layer. Information flows are tracked and can be inspected via `get_information_flows()`.

### Streaming Output (Default Behavior)
**The system now defaults to streaming output for better user experience:**
- CLI interface uses `process_stream()` by default
- Gradio interface supports streaming toggle (default: enabled)
- Real-time layer processing status and content generation
- Improved responsiveness for long-running queries

### System Creation Pattern
```python
# Recommended approach - New layered architecture with streaming
system = create_layered_system(
    system_type="educational",
    llm_provider="ollama", 
    llm_model_name="qwen3:8b"
)

# Initialize and use with streaming (recommended)
await system.initialize_layers()
async for chunk in system.process_stream(query, user_id, context):
    print(chunk, end="", flush=True)

# Alternative: Traditional batch processing
response = await system.process_through_layers(query, user_id, context)
```

### Memory Integration Pattern
The system uses **Graphiti** as the primary memory system, which provides:
- Neo4j graph database for persistent storage
- Temporal awareness with automatic timestamping
- Entity relationship tracking across conversations
- Hybrid search combining semantic similarity and graph traversal

### Error Handling & Graceful Degradation
- Memory system failures → Continue without memory
- Collaboration layer failures → Continue with core 3 layers
- Individual layer failures → Stop processing with detailed error info

## Configuration Management

### Environment Variables
The project uses environment variables for all configuration. Key variables include:

**LLM Configuration:**
- `DEFAULT_LLM_PROVIDER`: LLM provider (default: "ollama")
- `DEFAULT_LLM_MODEL`: Model name (default: "qwen3:8b")
- `DEFAULT_LLM_TEMPERATURE`: Temperature (default: "0.7")
- `DEFAULT_LLM_MAX_TOKENS`: Max tokens (default: "800")
- `OLLAMA_BASE_URL`: Ollama service URL (default: "http://localhost:11434")

**System Configuration:**
- `DEFAULT_SYSTEM_TYPE`: System type (default: "educational")
- `DEFAULT_MEMORY_SYSTEM`: Memory system (default: "graphiti")
- `ENABLE_MEMORY_SYSTEM`: Enable memory (default: "true")
- `ENABLE_STREAMING_OUTPUT`: Enable streaming (default: "true")
- `ENABLE_COLLABORATION_LAYER`: Enable collaboration (default: "true")

**Gradio Interface:**
- `GRADIO_SERVER_NAME`: Server host (default: "0.0.0.0")
- `GRADIO_SERVER_PORT`: Server port (default: "7860")
- `GRADIO_SHARE`: Public sharing (default: "false")

**Graphiti Configuration:**
- `GRAPHITI_API_URL`: Graphiti service URL (default: "http://localhost:8000")
- `NEO4J_URI`: Neo4j database URI (default: "bolt://localhost:7687")
- `NEO4J_USER`: Neo4j username (default: "neo4j")
- `NEO4J_PASSWORD`: Neo4j password (default: "neo4j_passwd")

### Configuration Usage
```python
from aienhance.config import config

# Get configuration values
llm_config = config.get_llm_config()
system_config = config.get_system_config()

# Print configuration summary
config.print_config_summary()
```

## Development Guidelines

### File Organization
- Core system: `aienhance/core/`
- Individual layers: `aienhance/{perception,cognition,behavior,collaboration}/`
- Adapters: `aienhance/{memory,llm}/adapters/`
- Tests: `tests/` (organized by component)
- Scripts: `scripts/` (setup and utility scripts)
- Docker configs: `docker/`

### Testing Strategy
Tests are organized by system component:
- `test_system_architecture.py`: Core system testing
- `test_*_integration.py`: Integration tests for specific components
- `test_*_layer.py`: Individual layer testing

### Configuration Management
All configuration is handled through:
- `ModelConfig` objects for LLM providers
- `MemorySystemConfig` objects for memory systems
- System-specific configs passed to layer constructors

### Dependencies
- **Core**: Python 3.12.9+, asyncio-based async architecture
- **Memory**: Graphiti service via HTTP API (aiohttp>=3.8.0)
- **LLM**: Multiple provider support via unified interface
- **Web UI**: Gradio with Plotly for visualizations
- **Code Quality**: Ruff for linting and formatting

## Project Context & History

This system evolved from traditional RAG to a **memory-cognitive synergy model**. The current architecture (v2.0) implements explicit layer objects for better modularity and information flow tracking. The legacy architecture is still available but not recommended for new development.

The project prioritizes:
1. **Temporal knowledge graphs** - Graphiti provides persistent memory with temporal relationships
2. **Graceful degradation** - Continues working even with component failures  
3. **Modular design** - Each layer is independently testable and configurable
4. **Memory-cognitive synergy** - Beyond retrieval, implements memory activation and semantic enhancement

When working with this codebase, always use the layered architecture approach and ensure proper async/await patterns throughout.