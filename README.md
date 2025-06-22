# Pydantic AI Agent Framework

A comprehensive framework for building production-grade AI agents using Pydantic AI, designed for non-coders with a user-friendly web interface.

## Features

- **Web-based Interface**: Easy-to-use frontend for managing AI agents without coding
- **Multi-Model Support**: Works with OpenAI, Anthropic, Gemini, and other LLM providers
- **Agent Management**: Create, configure, and monitor multiple AI agents
- **Template System**: Pre-built agent templates for common use cases
- **Structured Responses**: Pydantic validation ensures consistent outputs
- **Real-time Monitoring**: Track agent performance and conversations
- **Modular Design**: Easy integration with other projects

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   ```bash
   export OPENAI_API_KEY=your-api-key
   # or
   export ANTHROPIC_API_KEY=your-api-key
   ```

3. **Run the Application**
   ```bash
   python app.py
   ```

4. **Open Web Interface**
   Navigate to `http://localhost:8000` in your browser

## Project Structure

```
├── app.py                 # Main FastAPI application
├── frontend/              # Web interface files
├── agents/                # Agent definitions and templates
├── config/                # Configuration files
├── utils/                 # Utility functions
├── templates/             # HTML templates
└── static/                # CSS, JS, and other static files
```

## Usage

### Creating an Agent

1. Open the web interface
2. Click "Create New Agent"
3. Choose a template or create from scratch
4. Configure the agent's system prompt and tools
5. Test the agent in the chat interface

### Managing Agents

- View all agents in the dashboard
- Edit agent configurations
- Monitor conversation history
- Export/import agent configurations

## Integration with Other Projects

This framework is designed to be modular. You can:

1. **Import as a Package**: Use the agent classes in your own projects
2. **API Integration**: Connect to the REST API endpoints
3. **Configuration Export**: Export agent configs for use elsewhere

## Configuration

Edit `config/settings.yaml` to customize:

- Default LLM models
- API endpoints
- UI preferences
- Security settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details
