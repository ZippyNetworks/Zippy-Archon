# Zippy Archon - Hybrid AI Agent Framework

<p align="center">
  <img src="./archon-ui-main/public/archon-main-graphic.png" alt="Archon Main Graphic" width="853" height="422">
</p>

<p align="center">
  <em>Power up your AI coding assistants with your own custom knowledge base, task management, and advanced agentic workflows</em>
</p>

## 🎯 What is Zippy Archon?

Zippy Archon is a hybrid framework that combines the latest Archon V6 capabilities with advanced agentic workflow features. This fork extends the original Archon project with sophisticated plugin management, intelligent error handling, and enhanced orchestration capabilities.

### Key Features

**From Archon V6:**
- **MCP Server**: Model Context Protocol server for AI coding assistants
- **Knowledge Management**: Crawl websites, upload documents, and manage knowledge bases
- **Task Management**: Integrated project and task management
- **Modern Web UI**: React-based interface with real-time updates
- **Multi-LLM Support**: OpenAI, Anthropic, Ollama, and more

**Enhanced with Agentic Workflow:**
- **Plugin System**: Dynamic plugin loading and management
- **Intelligent Orchestration**: Advanced agent coordination and routing
- **Diagnostic Agents**: Self-healing error detection and resolution
- **Tool Generation**: AI-powered tool creation and integration
- **Enhanced Reasoning**: Sophisticated decision-making capabilities

## 🏗️ Architecture

This hybrid approach provides two main modes of operation:

### 1. Archon V6 Mode (Default)
The standard Archon V6 experience with knowledge management, task management, and MCP server capabilities.

### 2. Agentic Workflow Mode
Advanced agentic workflow system for building and orchestrating AI agents with:
- Plugin-based tool integration
- Intelligent error handling and recovery
- Dynamic agent creation and management
- Enhanced reasoning and decision-making

## 🚀 Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Node.js 18+](https://nodejs.org/) (for hybrid development mode)
- [Supabase](https://supabase.com/) account (free tier or local Supabase both work)
- [OpenAI API key](https://platform.openai.com/api-keys) (Gemini and Ollama are supported too!)

### Setup Instructions

1. **Clone Repository**:
   ```bash
   git clone https://github.com/ZippyNetworks/Zippy-Archon.git
   cd Zippy-Archon
   ```

2. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Supabase credentials:
   # SUPABASE_URL=https://your-project.supabase.co
   # SUPABASE_SERVICE_KEY=your-service-key-here
   ```

3. **Database Setup**: In your [Supabase project](https://supabase.com/dashboard) SQL Editor, copy, paste, and execute the contents of `migration/complete_setup.sql`

4. **Start Services**:

   **Full Docker Mode (Recommended)**
   ```bash
   docker compose up --build -d
   ```

   This starts all core microservices:
   - **Server**: Core API and business logic (Port: 8181)
   - **MCP Server**: Protocol interface for AI clients (Port: 8051)
   - **Agents**: AI operations and streaming (Port: 8052)
   - **UI**: Web interface (Port: 3737)

5. **Configure API Keys**:
   - Open http://localhost:3737
   - Go to **Settings** → Select your LLM/embedding provider and set the API key
   - Test by uploading a document or crawling a website

## 🔧 Agentic Workflow Mode

To use the enhanced agentic workflow capabilities:

1. **Navigate to the agentic workflow directory**:
   ```bash
   cd agentic-workflow
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Configure your API keys and Supabase settings
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the agentic workflow**:
   ```bash
   # Start the Streamlit interface
   streamlit run streamlit_ui.py
   
   # Or run the LangGraph workflow directly
   python archon_graph.py
   ```

### Agentic Workflow Features

- **Plugin Management**: Dynamic loading and registration of tools
- **Diagnostic Agents**: Intelligent error detection and resolution
- **Tool Generation**: AI-powered creation of new tools and integrations
- **Enhanced Orchestration**: Sophisticated agent coordination and routing
- **Reasoning Engine**: Advanced decision-making and problem-solving

## 🧩 Plugin System

The enhanced plugin system allows you to easily add new tools and capabilities:

1. **Create a new plugin** in `agentic-workflow/plugins/`
2. **Implement the Tool protocol** with `name`, `description`, and `run` method
3. **Register your plugin** using the plugin manager
4. **Use your plugin** in agentic workflows

Example plugin structure:
```python
class MyCustomTool:
    name = "my_custom_tool"
    description = "A custom tool for specific tasks"
    
    def run(self, *args, **kwargs):
        # Your tool logic here
        return result
```

## 🔗 Integration with AI Coding Assistants

Connect your AI coding assistants (Claude Code, Cursor, etc.) to leverage both modes:

- **Knowledge Base**: Access crawled documentation and uploaded files
- **Task Management**: Create and manage project tasks
- **Agentic Workflows**: Build and orchestrate custom AI agents
- **Plugin Tools**: Use and create custom tools and integrations

## 📚 Documentation

- **[Archon V6 Documentation](docs/docs/)** - Complete documentation for the V6 features
- **[Agentic Workflow Guide](agentic-workflow/README.md)** - Guide to the enhanced agentic workflow
- **[Plugin Development](agentic-workflow/plugins/pluginTemplate.md)** - How to create custom plugins

## 🤝 Contributing

Contributions are welcome! Please feel free to submit Pull Requests for both:
- **Archon V6 improvements** - Standard Archon features
- **Agentic workflow enhancements** - Advanced agentic capabilities

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Original Archon**: Built by [Cole Medin](https://github.com/coleam00) and contributors
- **Agentic Workflow**: Enhanced with advanced orchestration and plugin capabilities
- **Community**: Thanks to all contributors and users who have helped shape this project

---

**Zippy Archon** - Where knowledge management meets intelligent agentic workflows.
