#!/usr/bin/env python3
"""
Pydantic AI Framework Integration Script

This script helps integrate the Pydantic AI Framework into existing projects.
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def create_cursorrules(target_dir):
    """Create .cursorrules file for Cursor AI integration."""
    cursorrules_content = """# .cursorrules

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

## Best Practices
- Use async/await for all agent operations
- Handle exceptions from AI API calls
- Log agent interactions for debugging
- Keep AI logic separate from business logic
"""
    
    cursorrules_path = target_dir / ".cursorrules"
    with open(cursorrules_path, 'w') as f:
        f.write(cursorrules_content)
    print(f"✅ Created .cursorrules file")

def create_composer_md(target_dir):
    """Create composer.md file for Cursor Composer."""
    composer_content = """# AI Agent Integration Instructions

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
"""
    
    composer_path = target_dir / "composer.md"
    with open(composer_path, 'w') as f:
        f.write(composer_content)
    print(f"✅ Created composer.md file")

def update_env_file(target_dir):
    """Update or create .env file with AI framework variables."""
    env_path = target_dir / ".env"
    env_additions = """
# AI Framework Configuration
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# AI Framework Database
AI_FRAMEWORK_DB_PATH=./ai-framework/data/agents.db
"""
    
    if env_path.exists():
        # Check if AI framework config already exists
        with open(env_path, 'r') as f:
            content = f.read()
        
        if "AI Framework Configuration" not in content:
            with open(env_path, 'a') as f:
                f.write(env_additions)
            print(f"✅ Updated existing .env file")
        else:
            print(f"ℹ️  .env file already contains AI framework configuration")
    else:
        with open(env_path, 'w') as f:
            f.write(env_additions.strip())
        print(f"✅ Created .env file")

def update_requirements(target_dir):
    """Update requirements.txt with AI framework dependencies."""
    requirements_path = target_dir / "requirements.txt"
    ai_requirements = [
        "pydantic-ai[examples]>=0.0.14",
        "pydantic>=2.0.0",
        "fastapi>=0.104.0",
        "sqlalchemy>=2.0.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.25.0"
    ]
    
    existing_requirements = []
    if requirements_path.exists():
        with open(requirements_path, 'r') as f:
            existing_requirements = [line.strip() for line in f.readlines()]
    
    # Add new requirements that don't already exist
    new_requirements = []
    for req in ai_requirements:
        package_name = req.split('>=')[0].split('[')[0]
        if not any(package_name in existing for existing in existing_requirements):
            new_requirements.append(req)
    
    if new_requirements:
        with open(requirements_path, 'a') as f:
            f.write('\n# AI Framework Dependencies\n')
            for req in new_requirements:
                f.write(f"{req}\n")
        print(f"✅ Updated requirements.txt with {len(new_requirements)} new dependencies")
    else:
        print(f"ℹ️  requirements.txt already contains AI framework dependencies")

def integrate_as_submodule(target_dir, repo_url):
    """Integrate the framework as a git submodule."""
    print(f"🔄 Adding framework as git submodule...")
    
    # Add submodule
    if not run_command(f"git submodule add {repo_url} ai-framework", target_dir):
        return False
    
    # Initialize and update submodule
    if not run_command("git submodule update --init --recursive", target_dir):
        return False
    
    # Install dependencies in the submodule
    framework_dir = target_dir / "ai-framework"
    if not run_command("python3 -m pip install -r requirements.txt", framework_dir):
        return False
    
    # Copy .env.example to .env in the framework
    env_example = framework_dir / ".env.example"
    env_file = framework_dir / ".env"
    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print(f"✅ Created .env file in ai-framework")
    
    return True

def integrate_copy_components(target_dir, framework_path):
    """Copy core components to the existing project."""
    print(f"🔄 Copying core components...")
    
    # Create directories
    ai_agents_dir = target_dir / "ai_agents"
    ai_agents_dir.mkdir(exist_ok=True)
    (ai_agents_dir / "utils").mkdir(exist_ok=True)
    (ai_agents_dir / "config").mkdir(exist_ok=True)
    
    # Copy core files
    core_files = [
        ("utils/agent_manager.py", "ai_agents/utils/agent_manager.py"),
        ("utils/config_manager.py", "ai_agents/utils/config_manager.py"),
        ("utils/database.py", "ai_agents/utils/database.py"),
        ("config/settings.py", "ai_agents/config/settings.py"),
    ]
    
    for src, dst in core_files:
        src_path = Path(framework_path) / src
        dst_path = target_dir / dst
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            print(f"✅ Copied {src}")
        else:
            print(f"⚠️  Warning: {src} not found")
    
    # Create __init__.py files
    (ai_agents_dir / "__init__.py").touch()
    (ai_agents_dir / "utils" / "__init__.py").touch()
    (ai_agents_dir / "config" / "__init__.py").touch()
    
    return True

def create_example_integration(target_dir):
    """Create an example integration file."""
    example_content = '''"""
Example integration of Pydantic AI Framework

This file shows how to use the AI framework in your existing project.
"""

import asyncio
import sys
from pathlib import Path

# Add the AI framework to the path (if using submodule method)
sys.path.append('./ai-framework')

try:
    from ai_framework.utils.agent_manager import AgentManager
    from ai_framework.utils.config_manager import ConfigManager
except ImportError:
    # If using copy method
    from ai_agents.utils.agent_manager import AgentManager
    from ai_agents.utils.config_manager import ConfigManager

async def example_usage():
    """Example of how to use the AI framework."""
    
    # Initialize the agent manager
    agent_manager = AgentManager()
    
    # Create a simple agent configuration
    agent_config = {
        "name": "Example Assistant",
        "description": "A helpful assistant for demonstration",
        "system_prompt": "You are a helpful assistant. Be concise and friendly.",
        "model_provider": "openai",
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    try:
        # Create the agent
        agent_id = await agent_manager.create_agent(agent_config)
        print(f"✅ Created agent with ID: {agent_id}")
        
        # Get the agent instance
        agent = await agent_manager.get_agent_instance(agent_id)
        
        # Use the agent
        result = await agent.run("Hello! Can you help me understand how to use this framework?")
        print(f"🤖 AI Response: {result.data}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have:")
        print("1. Added your API keys to the .env file")
        print("2. Installed the required dependencies")
        print("3. Set up the framework correctly")

def sync_example():
    """Synchronous wrapper for the async example."""
    asyncio.run(example_usage())

if __name__ == "__main__":
    sync_example()
'''
    
    example_path = target_dir / "ai_framework_example.py"
    with open(example_path, 'w') as f:
        f.write(example_content)
    print(f"✅ Created example integration file: ai_framework_example.py")

def main():
    parser = argparse.ArgumentParser(description="Integrate Pydantic AI Framework into existing project")
    parser.add_argument("--method", choices=["submodule", "copy"], default="submodule",
                       help="Integration method (default: submodule)")
    parser.add_argument("--repo-url", default="https://github.com/yourusername/pydantic-ai-framework.git",
                       help="Repository URL for submodule method")
    parser.add_argument("--framework-path", help="Path to framework for copy method")
    parser.add_argument("--target-dir", default=".", help="Target directory (default: current directory)")
    
    args = parser.parse_args()
    
    target_dir = Path(args.target_dir).resolve()
    
    print(f"🚀 Integrating Pydantic AI Framework into: {target_dir}")
    print(f"📋 Method: {args.method}")
    
    # Check if target directory exists and is a git repository
    if not target_dir.exists():
        print(f"❌ Target directory does not exist: {target_dir}")
        sys.exit(1)
    
    if args.method == "submodule" and not (target_dir / ".git").exists():
        print(f"❌ Target directory is not a git repository. Use --method copy instead.")
        sys.exit(1)
    
    try:
        # Perform integration based on method
        if args.method == "submodule":
            if not integrate_as_submodule(target_dir, args.repo_url):
                print(f"❌ Failed to integrate as submodule")
                sys.exit(1)
        elif args.method == "copy":
            if not args.framework_path:
                print(f"❌ --framework-path is required for copy method")
                sys.exit(1)
            if not integrate_copy_components(target_dir, args.framework_path):
                print(f"❌ Failed to copy components")
                sys.exit(1)
        
        # Create supporting files
        create_cursorrules(target_dir)
        create_composer_md(target_dir)
        update_env_file(target_dir)
        update_requirements(target_dir)
        create_example_integration(target_dir)
        
        print(f"\n🎉 Integration complete!")
        print(f"\nNext steps:")
        print(f"1. Edit .env file and add your API keys")
        print(f"2. Install dependencies: pip install -r requirements.txt")
        print(f"3. Run the example: python ai_framework_example.py")
        print(f"4. Check CURSOR_INTEGRATION.md for detailed usage instructions")
        
    except Exception as e:
        print(f"❌ Integration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
