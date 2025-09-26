#!/usr/bin/env python3
"""
Setup script for new users
"""
import os
import shutil
from pathlib import Path

def setup_environment():
    """Set up the environment for new users"""
    print("🚀 Setting up Agentic Stock AI")
    print("=" * 40)
    
    # Check if .env exists
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        shutil.copy(env_example, env_file)
        print(f"✅ Created {env_file}")
        print(f"📋 Please edit {env_file} and add your GEMINI_API_KEY")
        print("🔗 Get your API key from: https://aistudio.google.com/apikey")
    elif env_file.exists():
        print("✅ .env file already exists")
    
    # Check if API key is set
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Try to load from .env file
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        if api_key and api_key != "your_gemini_api_key_here":
                            os.environ["GEMINI_API_KEY"] = api_key
                            break
    
    if api_key and api_key != "your_gemini_api_key_here":
        print("✅ API key found")
        print("🧪 Running setup test...")
        os.system("python test_setup.py")
    else:
        print("⚠️  API key not found or not set")
        print("📝 Please edit .env file and add your GEMINI_API_KEY")
        print("🔗 Get your API key from: https://aistudio.google.com/apikey")
    
    print("\n" + "=" * 40)
    print("🎉 Setup complete!")
    print("💡 Run 'streamlit run streamlit_app.py' to start the web interface")

if __name__ == "__main__":
    setup_environment()