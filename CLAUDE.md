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

### SubModule Abstract Architecture

**BaseSubModule Template Method Pattern**

All submodules in the system follow a standardized architecture based on the **Template Method Pattern**. This provides consistent LLM-driven processing while allowing domain-specific customization.

#### Core Structure

```python
from aienhance.core.base_architecture import BaseSubModule, ProcessingContext, ProcessingResult

class YourSubModule(BaseSubModule):
    """Your domain-specific submodule"""
    
    def __init__(self, llm_adapter=None, config: dict[str, Any] | None = None):
        super().__init__("your_module_name", llm_adapter, config)
    
    async def _initialize_impl(self):
        """Module-specific initialization logic"""
        pass
    
    # ========== Required Abstract Methods ==========
    
    def _get_output_schema(self) -> dict:
        """Define JSON Schema for LLM structured output"""
        return {
            "type": "object",
            "properties": {
                "your_field": {"type": "string"},
                # ... define your schema
            },
            "required": ["your_field"]
        }
    
    async def _build_analysis_prompt(
        self, query: str, session_context: dict[str, Any], user_id: str
    ) -> str:
        """Build domain-specific analysis prompt"""
        return f"""
        You are a {self.name} expert. Analyze the following:
        
        User Query: {query}
        Context: {session_context}
        
        Please provide structured analysis...
        """
    
    async def _build_result_data(
        self, parsed_output: dict[str, Any], context: ProcessingContext
    ) -> dict[str, Any]:
        """Transform parsed LLM output into result data"""
        return {
            "analysis_result": parsed_output,
            "timestamp": context.metadata.get("created_at"),
            # ... your specific data fields
        }
    
    def _create_default_output(self, analysis_text: str = "") -> dict[str, Any]:
        """Create fallback output when LLM parsing fails"""
        return {
            "your_field": "default_value",
            "confidence_score": 0.3,
            "analysis_notes": f"Fallback analysis: {analysis_text[:200]}..."
        }
    
    # ========== Optional Helper Methods ==========
    
    def _build_result_metadata(
        self, parsed_output: dict[str, Any], analysis_prompt: str
    ) -> dict[str, Any]:
        """Build metadata for the processing result (optional override)"""
        return {
            "submodule": self.name,
            "prompt_tokens": len(analysis_prompt.split()),
            # ... your specific metadata
        }
```

#### Processing Flow

The base class provides a standardized `process()` method that:

1. **Calls** `_build_analysis_prompt()` to generate domain-specific prompt
2. **Gets** JSON schema from `_get_output_schema()`
3. **Executes** LLM streaming with JSON Schema constraint
4. **Parses** LLM output using schema validation
5. **Falls back** to `_create_default_output()` if parsing fails
6. **Builds** result data via `_build_result_data()`
7. **Returns** `ProcessingResult` with success/failure status

#### Implementation Guidelines

**✅ DO:**
- Use `dict[str, Any]` instead of `Dict[str, Any]` for type annotations
- Include `| None` for optional config parameters: `config: dict[str, Any] | None = None`
- Make JSON schemas comprehensive with proper validation rules
- Include confidence scores and analysis notes in outputs
- Use async/await for all processing methods
- Log important processing milestones
- Preserve existing helper methods during refactoring

**❌ DON'T:**
- Implement your own `process()` method - use the base class template
- Include manual LLM streaming or JSON parsing logic
- Import unused classes like `ProcessingResult` in submodules
- Use blocking I/O operations in async methods
- Skip error handling in custom helper methods

#### Migration from Legacy Submodules

When refactoring existing submodules to use BaseSubModule:

1. **Remove** the existing `process()` method
2. **Convert** `_get_*_schema()` → `_get_output_schema()`
3. **Convert** `_build_*_prompt()` → `_build_analysis_prompt()`
4. **Add** missing abstract methods: `_build_result_data()`, `_create_default_output()`
5. **Remove** duplicate JSON parsing and LLM streaming code
6. **Keep** domain-specific helper methods
7. **Fix** type annotations and imports
8. **Test** thoroughly with verification script

#### Examples of Refactored Submodules

**Successfully Refactored:**
- `CognitiveAbilityModelingSubModule` - Cognitive analysis with thinking style assessment
- `CognitiveNeedsPredictionSubModule` - Learning preference prediction
- `ContextElementsExtractionSubModule` - 8-dimensional context analysis
- `InteractionPatternModelingSubModule` - User interaction behavior modeling
- `KnowledgeStructureModelingSubModule` - Domain expertise and knowledge graph construction

Each refactored module eliminated 50-90 lines of duplicate infrastructure code while preserving all domain-specific business logic.

### Working with LLM
**LLM developing best practice**
- Use STREAMING style when calling LLM
- Use JSON SCHEMA to constrain the format of LLM output 
- All submodules automatically get streaming + JSON Schema via BaseSubModule

### use LATEST API docs
- If you think this API interface cannot implement the specified function, first use the MCP tool (context7) to check the latest API documentation.

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
- 当前处于程序开发的早期，程序结构并不稳定。在生成相应的测试程序时，应只生成主要函数入口的测试，而不是所有函数入口。
- 注意当前的测试更多是为了构造一个可运行环境，而不是健壮性

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