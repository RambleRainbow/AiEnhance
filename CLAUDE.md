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

### Running the Application
```bash
# Command-line interface
uv run python cli_example.py "your question here"
uv run python cli_example.py -i  # Interactive mode

# Web interface (Gradio)
uv run python gradio_interface.py
# Access at http://localhost:7860
```

### Code Quality & Linting
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
- `create_enhanced_system()`: Legacy architecture (still supported)

**System Types:**
- `educational`: Optimized for learning scenarios
- `research`: Enhanced analytical capabilities
- `creative`: Higher temperature, creative thinking
- `lightweight`: Minimal resource usage, no collaboration layer

### Memory System Integration

**MIRIX Integration** (Recommended):
- `mirix_unified_adapter.py`: Uses project's LLM abstraction (no separate API key needed)
- Unified LLM mode: Single model serves both chat and memory functions
- Automatic fallback to no-memory mode if MIRIX unavailable

**Alternative Memory Systems:**
- `mem0_adapter.py`: Mem0 integration
- `graphiti_adapter.py`: Graphiti integration

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

### System Creation Pattern
```python
# Recommended approach - New layered architecture
system = create_layered_system(
    system_type="educational",
    llm_provider="ollama", 
    llm_model_name="qwen3:8b"
)

# Initialize and use
await system.initialize_layers()
response = await system.process_through_layers(query, user_id, context)
```

### Memory Integration Pattern
The system uses a **unified LLM approach** where the same LLM serves both chat and memory functions, eliminating the need for separate Google API keys for MIRIX.

### Error Handling & Graceful Degradation
- Memory system failures → Continue without memory
- Collaboration layer failures → Continue with core 3 layers
- Individual layer failures → Stop processing with detailed error info

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
- **Memory**: MIRIX SDK (mirix>=0.1.0)
- **LLM**: Multiple provider support via unified interface
- **Web UI**: Gradio with Plotly for visualizations
- **Code Quality**: Ruff for linting and formatting

## Project Context & History

This system evolved from traditional RAG to a **memory-cognitive synergy model**. The current architecture (v2.0) implements explicit layer objects for better modularity and information flow tracking. The legacy architecture is still available but not recommended for new development.

The project prioritizes:
1. **Unified LLM management** - Single model for all functions
2. **Graceful degradation** - Continues working even with component failures  
3. **Modular design** - Each layer is independently testable and configurable
4. **Memory integration** - Beyond retrieval, implements memory activation and semantic enhancement

When working with this codebase, always use the layered architecture approach and ensure proper async/await patterns throughout.