# Integrating Pydantic AI Framework with Existing Cursor Projects

This guide shows you how to integrate the Pydantic AI Agent Framework into your existing projects in Cursor IDE.

## Integration Methods

### Method 1: As a Submodule (Recommended)

This keeps the framework separate but accessible from your main project.

```bash
# Navigate to your existing project
cd /path/to/your/existing/project

# Add the framework as a git submodule
git submodule add https://github.com/yourusername/pydantic-ai-framework.git ai-framework

# Initialize and update the submodule
git submodule update --init --recursive

# Install the framework dependencies
cd ai-framework
python3 -m pip install -r requirements.txt

# Copy the environment template
cp .env.example .env
# Edit .env and add your API keys
```

**Usage in your project:**
```python
# In your existing project files
import sys
sys.path.append('./ai-framework')

from ai_framework.utils.agent_manager import AgentManager
from ai_framework.utils.config_manager import ConfigManager

# Use the framework
agent_manager = AgentManager()
# ... rest of your code
```

### Method 2: Copy Core Components

Copy only the essential parts you need into your existing project.

```bash
# In your existing project directory
mkdir ai_agents
mkdir ai_agents/utils
mkdir ai_agents/config

# Copy core files
cp /path/to/pydantic-ai-framework/utils/agent_manager.py ai_agents/utils/
cp /path/to/pydantic-ai-framework/utils/config_manager.py ai_agents/utils/
cp /path/to/pydantic-ai-framework/utils/database.py ai_agents/utils/
cp /path/to/pydantic-ai-framework/config/settings.py ai_agents/config/

# Add to your requirements.txt
echo "pydantic-ai[examples]>=0.0.14" >> requirements.txt
echo "pydantic>=2.0.0" >> requirements.txt
echo "fastapi>=0.104.0" >> requirements.txt
echo "sqlalchemy>=2.0.0" >> requirements.txt
```

### Method 3: Package Installation (Future)

Once published as a package:

```bash
pip install pydantic-ai-framework
```

```python
from pydantic_ai_framework import AgentManager, ConfigManager
```

## Cursor-Specific Integration

### 1. Using Cursor's AI Features with the Framework

Create a `.cursorrules` file in your project root:

```markdown
# .cursorrules

## Pydantic AI Framework Integration

When working with AI agents in this project:

1. Use the AgentManager from `ai-framework/utils/agent_manager.py`
2. All agent configurations should be stored in `ai-framework/agents/`
3. Follow the Pydantic AI patterns for tool definitions
4. Use the existing database schema in `ai-framework/utils/database.py`

## Code Patterns

### Creating an Agent
```python
from ai_framework.utils.agent_manager import AgentManager

agent_manager = AgentManager()
agent_config = {
    "name": "My Agent",
    "description": "Agent description",
    "system_prompt": "You are a helpful assistant",
    "model_provider": "openai",
    "model_name": "gpt-4",
    "temperature": 0.7
}
agent_id = await agent_manager.create_agent(agent_config)
```

### Using an Agent
```python
agent = await agent_manager.get_agent_instance(agent_id)
result = await agent.run("Hello, how can you help me?")
print(result.data)
```
```

### 2. Environment Setup in Cursor

Add to your existing `.env` file:

```bash
# AI Framework Configuration
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GEMINI_API_KEY=your-gemini-api-key

# AI Framework Database
AI_FRAMEWORK_DB_PATH=./ai-framework/data/agents.db
```

### 3. Cursor Composer Integration

Create a `composer.md` file for Cursor Composer:

```markdown
# AI Agent Integration Instructions

## Context
This project uses the Pydantic AI Agent Framework for AI functionality.

## Key Files
- `ai-framework/utils/agent_manager.py` - Main agent management
- `ai-framework/utils/config_manager.py` - Configuration handling
- `ai-framework/agents/` - Agent configurations
- `ai-framework/data/` - Database and data storage

## Common Tasks

### Add a new AI feature
1. Create agent configuration in `ai-framework/agents/`
2. Use AgentManager to load and run the agent
3. Handle responses in your application logic

### Modify agent behavior
1. Update the agent's system prompt
2. Adjust temperature and model settings
3. Add or remove tools as needed

## Code Style
- Use async/await for all agent operations
- Handle exceptions from AI API calls
- Log agent interactions for debugging
```

## Integration Examples

### Example 1: Adding AI Chat to a Web App

```python
# In your existing Flask/FastAPI app
from ai_framework.utils.agent_manager import AgentManager

app = FastAPI()  # or Flask()
agent_manager = AgentManager()

@app.post("/chat")
async def chat_endpoint(message: str, agent_id: str):
    try:
        agent = await agent_manager.get_agent_instance(agent_id)
        result = await agent.run(message)
        return {"response": result.data}
    except Exception as e:
        return {"error": str(e)}
```

### Example 2: Adding AI to a Data Processing Pipeline

```python
# In your existing data processing script
import asyncio
from ai_framework.utils.agent_manager import AgentManager

async def process_data_with_ai(data):
    agent_manager = AgentManager()
    
    # Load a specialized data analysis agent
    agent = await agent_manager.get_agent_instance("data-analyst-agent")
    
    # Process each data item
    results = []
    for item in data:
        prompt = f"Analyze this data: {item}"
        result = await agent.run(prompt)
        results.append(result.data)
    
    return results

# Use in your existing pipeline
data = load_your_data()
ai_results = asyncio.run(process_data_with_ai(data))
```

### Example 3: Adding AI to a CLI Tool

```python
# In your existing CLI application
import click
from ai_framework.utils.agent_manager import AgentManager

@click.command()
@click.option('--agent', default='general-assistant', help='Agent to use')
@click.option('--message', prompt='Your message', help='Message to send to AI')
def chat(agent, message):
    """Chat with an AI agent from the command line."""
    async def run_chat():
        agent_manager = AgentManager()
        agent_instance = await agent_manager.get_agent_instance(agent)
        result = await agent_instance.run(message)
        click.echo(f"AI: {result.data}")
    
    import asyncio
    asyncio.run(run_chat())

if __name__ == '__main__':
    chat()
```

## Project Structure After Integration

```
your-existing-project/
├── your-existing-files/
├── ai-framework/                 # Submodule
│   ├── utils/
│   ├── agents/
│   ├── data/
│   └── ...
├── .cursorrules                  # Cursor AI instructions
├── composer.md                   # Composer instructions
├── .env                         # Updated with AI keys
└── requirements.txt             # Updated with AI dependencies
```

## Best Practices

### 1. Separation of Concerns
- Keep AI logic in the framework
- Keep business logic in your main project
- Use clear interfaces between them

### 2. Configuration Management
- Store agent configurations in the framework
- Use environment variables for API keys
- Keep sensitive data out of version control

### 3. Error Handling
```python
async def safe_ai_call(agent_id: str, message: str):
    try:
        agent = await agent_manager.get_agent_instance(agent_id)
        result = await agent.run(message)
        return {"success": True, "data": result.data}
    except Exception as e:
        logger.error(f"AI call failed: {e}")
        return {"success": False, "error": str(e)}
```

### 4. Testing
```python
# Test your AI integration
import pytest
from ai_framework.utils.agent_manager import AgentManager

@pytest.mark.asyncio
async def test_ai_integration():
    agent_manager = AgentManager()
    agent = await agent_manager.get_agent_instance("test-agent")
    result = await agent.run("Hello")
    assert result.data is not None
```

## Cursor Workflow Tips

### 1. Use Cursor's AI for Agent Creation
- Ask Cursor to help create agent configurations
- Use Cursor to generate system prompts
- Let Cursor help with tool definitions

### 2. Debugging with Cursor
- Use Cursor's debugging features to step through AI calls
- Set breakpoints in agent_manager.py
- Use Cursor's variable inspection for AI responses

### 3. Code Generation
- Use Cursor Composer to generate integration code
- Ask Cursor to create wrapper functions for your use cases
- Generate test cases for AI functionality

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure the submodule is properly initialized
   git submodule update --init --recursive
   ```

2. **API Key Issues**
   ```bash
   # Check your .env file has the correct keys
   cat .env | grep API_KEY
   ```

3. **Database Issues**
   ```bash
   # Reset the AI framework database
   rm ai-framework/data/agents.db
   ```

### Getting Help

1. Check the main implementation guide: `implementation-guide.html`
2. Review the framework documentation: `SETUP.md`
3. Use Cursor's AI to help debug integration issues
4. Create issues in the GitHub repository

## Next Steps

1. Choose your integration method
2. Set up the framework in your project
3. Create your first agent
4. Test the integration
5. Build your AI-powered features!

The framework is designed to be flexible and work with any existing Python project. Choose the integration method that best fits your project structure and requirements.
