# Pydantic AI Agent Framework - Setup Guide

This guide will help you set up and run the Pydantic AI Agent Framework on your system.

## Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)
- An API key from at least one LLM provider (OpenAI, Anthropic, or Google Gemini)

## Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/pydantic-ai-framework.git
cd pydantic-ai-framework
```

### 2. Run the Setup Script

```bash
python3 setup.py
```

This will:
- Create necessary directories
- Install all required dependencies
- Create a `.env` file from the example

### 3. Configure API Keys

Edit the `.env` file and add your API keys:

```bash
# For OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# For Anthropic (optional)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# For Google Gemini (optional)
GEMINI_API_KEY=your-gemini-api-key-here
```

### 4. Start the Application

```bash
python3 app.py
```

The application will start on `http://localhost:8000`

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and add your API keys.

### 3. Create Directories

```bash
mkdir -p agents/templates config data logs static/css static/js templates utils
```

### 4. Run the Application

```bash
python3 app.py
```

## Getting API Keys

### OpenAI
1. Go to [OpenAI API](https://platform.openai.com/api-keys)
2. Create an account or sign in
3. Generate a new API key
4. Add it to your `.env` file as `OPENAI_API_KEY`

### Anthropic
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Generate an API key
4. Add it to your `.env` file as `ANTHROPIC_API_KEY`

### Google Gemini
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an account or sign in
3. Generate an API key
4. Add it to your `.env` file as `GEMINI_API_KEY`

## Using the Framework

### 1. Access the Web Interface

Open your browser and go to `http://localhost:8000`

### 2. Create Your First Agent

1. Click "Create New Agent" on the dashboard
2. Choose a template or create from scratch
3. Configure the agent's name, description, and system prompt
4. Select a model provider and model
5. Adjust temperature and token settings as needed
6. Save the agent

### 3. Chat with Your Agent

1. Click the "Chat" button on any agent card
2. Start typing messages in the chat interface
3. The agent will respond based on its configuration

### 4. Manage Agents

- **View All Agents**: Go to the "Agents" page
- **Edit Agent**: Click the three dots menu on any agent card
- **Export Configuration**: Download agent settings as JSON
- **Import Agent**: Upload a previously exported configuration

## Features

### Agent Templates
The framework comes with pre-built templates:
- **General Assistant**: A helpful general-purpose AI
- **Code Assistant**: Specialized for programming tasks
- **Research Assistant**: Optimized for information gathering
- **Math Tutor**: Focused on mathematical problem-solving

### Tools Integration
Agents can be equipped with tools:
- **Web Search**: Search the internet for information
- **Calculator**: Perform mathematical calculations
- **File Reader**: Read and analyze files

### Conversation Management
- **History**: All conversations are automatically saved
- **Export**: Download chat transcripts
- **Statistics**: View usage metrics and performance data

## Integration with Other Projects

### As a Python Package

```python
from utils.agent_manager import AgentManager
from utils.config_manager import ConfigManager

# Initialize managers
agent_manager = AgentManager()
config_manager = ConfigManager()

# Load an agent
agent_config = await agent_manager.get_agent("agent_id")
agent_instance = await agent_manager.create_agent_instance(agent_config)

# Use the agent
result = await agent_instance.run("Hello, how are you?")
print(result.data)
```

### Via REST API

```bash
# Get all agents
curl http://localhost:8000/api/agents

# Chat with an agent
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "your-agent-id", "message": "Hello!"}'

# Export agent configuration
curl http://localhost:8000/api/agents/your-agent-id/export
```

### Configuration Export/Import

Export agent configurations as JSON files that can be:
- Shared with team members
- Version controlled
- Used in other projects
- Imported into different instances

## Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Make sure all dependencies are installed
pip install -r requirements.txt
```

**2. API Key Errors**
- Verify your API keys are correct in the `.env` file
- Check that you have sufficient credits/quota with your provider
- Ensure the API key has the necessary permissions

**3. Port Already in Use**
```bash
# Change the port in .env file
PORT=8001
```

**4. Database Issues**
```bash
# Remove the database file to reset
rm data/agents.db
```

### Getting Help

1. Check the [GitHub Issues](https://github.com/yourusername/pydantic-ai-framework/issues)
2. Review the [Pydantic AI Documentation](https://ai.pydantic.dev/)
3. Create a new issue with detailed error information

## Development

### Running in Development Mode

```bash
# Enable debug mode in .env
DEBUG=True

# Run with auto-reload
python3 app.py
```

### Code Formatting

```bash
# Format code
black .
isort .
```

### Testing

```bash
# Run tests
pytest
```

## Production Deployment

### Environment Variables

Set these in production:
```bash
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-production-database-url
```

### Using Docker (Optional)

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t pydantic-ai-framework .
docker run -p 8000:8000 pydantic-ai-framework
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Acknowledgments

- Built with [Pydantic AI](https://ai.pydantic.dev/)
- Web interface powered by [FastAPI](https://fastapi.tiangolo.com/)
- Frontend uses [Bootstrap](https://getbootstrap.com/)
