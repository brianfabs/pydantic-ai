"""
Setup script for Pydantic AI Agent Framework
"""

import os
import sys
import subprocess
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = [
        "agents",
        "agents/templates", 
        "config",
        "data",
        "logs",
        "static",
        "static/css",
        "static/js",
        "templates",
        "utils"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    return True

def create_env_file():
    """Create .env file from example if it doesn't exist"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file from .env.example")
            print("⚠️  Please edit .env file and add your API keys")
        else:
            print("❌ .env.example file not found")
    else:
        print("✅ .env file already exists")

def main():
    """Main setup function"""
    print("🤖 Pydantic AI Agent Framework Setup")
    print("=" * 40)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        return
    
    # Create environment file
    create_env_file()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit the .env file and add your API keys")
    print("2. Run: python app.py")
    print("3. Open http://localhost:8000 in your browser")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()
