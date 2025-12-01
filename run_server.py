#!/usr/bin/env python3
"""
Script to run the RAG API server with proper environment loading.
"""
import os
from pathlib import Path

# Load environment variables from .env file
dotenv_loaded = False
print(f"-------------------------------------------------")

try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file, override=True)
        dotenv_loaded = True
        print(f"✅ Loaded configuration from {env_file}")
    else:
        print("⚠️  No .env file found - using system environment variables")
except ImportError:
    print("⚠️  python-dotenv not installed - using system environment variables")

# Validate required configuration
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key == "your-actual-api-key-here":
    print("❌ OPENAI_API_KEY not set or still using placeholder!")
    print("   Please edit .env file and set your real OpenAI API key")
    exit(1)

print(f"✅ API key configured (starts with: {api_key[:10]}...)")

print(f"📁 FAQ Directory: {os.getenv('FAQ_DIR', 'faqs')}")
print(f"🤖 LLM Model: {os.getenv('LLM_MODEL', 'gpt-3.5-turbo')}")
print(f"🔍 Embedding Model: {os.getenv('EMBED_MODEL', 'text-embedding-ada-002')}")

# Start the server
if __name__ == "__main__":
    print("🎯 To enable Datadog auto-instrumentation, use:")
    print("   ddtrace-run python run_server.py")
    print("   OR")
    print("   ddtrace-run uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload")
    print("-------------------------------------------------")
    
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
