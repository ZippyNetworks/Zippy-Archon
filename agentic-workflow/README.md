# Agentic Workflow - Advanced AI Agent Orchestration

This directory contains the enhanced agentic workflow system that extends the original Archon V2 with sophisticated plugin management, intelligent error handling, and advanced orchestration capabilities.

## 🎯 Overview

The Agentic Workflow system is designed to be a "master tool" that can:
- Accept high-level prompts and automatically spin up specialized agents
- Dynamically load and manage plugins and tools
- Handle errors intelligently with self-healing capabilities
- Continuously learn and adapt based on experience
- Orchestrate complex multi-agent workflows

## 🏗️ Architecture

### Core Components

1. **Orchestrator** (`orchestrator.py`)
   - Master workflow controller
   - Manages agent coordination and routing
   - Handles dynamic workflow creation

2. **Plugin System** (`plugins/`)
   - Dynamic tool loading and registration
   - Standardized plugin interface
   - Hot-swappable capabilities

3. **Diagnostic Agents** (`diagnostic_agent.py`)
   - Intelligent error detection and resolution
   - Self-healing capabilities
   - Problem diagnosis and recovery

4. **Tool Generator** (`tool_generator_agent.py`)
   - AI-powered tool creation
   - Automatic code generation
   - Integration testing

5. **Enhanced Graph** (`archon_graph.py`)
   - LangGraph-based workflow definition
   - Advanced state management
   - Conditional routing and decision making

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Supabase account and database
- OpenAI/OpenRouter API key or Ollama for local LLMs
- Streamlit (for web interface)

### Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and preferences
   ```

3. **Database setup**:
   - Execute the SQL commands in `site_pages.sql` in your Supabase SQL Editor

4. **Run the system**:
   ```bash
   # Start the Streamlit interface
   streamlit run streamlit_ui.py
   
   # Or run the LangGraph workflow directly
   python archon_graph.py
   ```

## 🧩 Plugin System

### Creating Plugins

1. **Create a new plugin file** in `plugins/`:
   ```python
   # plugins/my_custom_tool.py
   
   class MyCustomTool:
       name = "my_custom_tool"
       description = "A custom tool for specific tasks"
       
       def run(self, *args, **kwargs):
           # Your tool logic here
           return result
   ```

2. **Register your plugin**:
   ```python
   from plugins.plugin_manager import register_tool
   from plugins.my_custom_tool import MyCustomTool
   
   # Register the tool
   register_tool(MyCustomTool())
   ```

3. **Use in workflows**:
   ```python
   from plugins.plugin_manager import get_tool_by_name
   
   tool = get_tool_by_name("my_custom_tool")
   result = tool.run(your_parameters)
   ```

### Plugin Template

See `plugins/pluginTemplate.md` for a detailed template and examples.

## 🔧 Advanced Features

### Intelligent Error Handling

The diagnostic agent can:
- Detect common error patterns
- Suggest solutions and workarounds
- Automatically retry with different approaches
- Learn from previous errors to prevent recurrence

### Dynamic Tool Generation

The tool generator can:
- Create new tools based on requirements
- Generate code for custom integrations
- Test and validate new tools
- Integrate tools into existing workflows

### Enhanced Orchestration

The orchestrator provides:
- Dynamic workflow creation
- Intelligent agent routing
- State management and persistence
- Real-time progress tracking

## 📊 Usage Examples

### Basic Workflow

```python
from orchestrator import Orchestrator

# Create orchestrator instance
orchestrator = Orchestrator()

# Start a new workflow
orchestrator.start_flow("Build me a Slack integration that notifies the team when a new lead arrives")
```

### Custom Plugin Integration

```python
from plugins.plugin_manager import load_plugins, get_tool_by_name

# Load all plugins
load_plugins("plugins/")

# Use a specific tool
slack_tool = get_tool_by_name("slack_notification")
result = slack_tool.run(message="New lead received!", channel="#leads")
```

### Error Recovery

```python
from diagnostic_agent import diagnose_errors

# When an error occurs, the system can automatically diagnose and recover
diagnosis = await diagnose_errors(error_context)
if diagnosis.can_recover:
    recovery_action = diagnosis.suggested_action
    # Execute recovery
```

## 🔗 Integration with Archon V6

The agentic workflow can integrate with the main Archon V6 system:

1. **Knowledge Base Access**: Use crawled documentation and uploaded files
2. **Task Management**: Create and manage project tasks
3. **MCP Server**: Expose agentic workflow capabilities via MCP
4. **Web UI**: Access through the main Archon interface

## 📚 API Reference

### Orchestrator Class

```python
class Orchestrator:
    def __init__(self)
    def start_flow(self, user_message: str)
    def resume_flow(self, user_message: str)
    def get_current_state(self) -> AgentState
```

### Plugin Manager

```python
def register_tool(tool: Tool)
def load_plugins(plugins_dir: str)
def get_tool_by_name(name: str) -> Optional[Tool]
```

### Diagnostic Agent

```python
async def diagnose_errors(error_context: dict) -> Diagnosis
```

## 🛠️ Development

### Adding New Agents

1. Create your agent class
2. Implement the required interface
3. Add to the orchestrator workflow
4. Test with the diagnostic system

### Extending the Plugin System

1. Define new plugin interfaces
2. Update the plugin manager
3. Add validation and testing
4. Document the new capabilities

### Testing

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=.
```

## 🔍 Troubleshooting

### Common Issues

1. **Plugin Loading Errors**
   - Check plugin implements the Tool protocol
   - Verify plugin file is in the correct directory
   - Check for import errors

2. **Workflow State Issues**
   - Clear the memory checkpoint
   - Restart the orchestrator
   - Check for state corruption

3. **API Key Issues**
   - Verify API keys in .env file
   - Check rate limits and quotas
   - Test with different providers

### Debug Mode

Enable debug logging by setting:
```bash
LOG_LEVEL=DEBUG
```

## 📈 Future Enhancements

- **Multi-tenant Support**: Isolated workflows per user/organization
- **Advanced Reasoning**: More sophisticated decision-making capabilities
- **Performance Optimization**: Caching and parallel processing
- **Extended Plugin Ecosystem**: More built-in tools and integrations
- **Visual Workflow Builder**: Drag-and-drop workflow creation

## 🤝 Contributing

Contributions to the agentic workflow system are welcome! Please:

1. Follow the existing code patterns
2. Add tests for new features
3. Update documentation
4. Test with the diagnostic system

## 📄 License

This component is part of Zippy Archon and follows the same MIT license as the main project.
