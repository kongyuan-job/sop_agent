import os
from dotenv import load_dotenv
from src.agent_engine import AgentEngine
from src.builtin_tools import DEFAULT_TOOLS

# Load environment variables from .env file
load_dotenv()

def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it using: set OPENAI_API_KEY=your_key_here")
        return

    # Initialize Agent (skills are auto-discovered but loaded on-demand)
    engine = AgentEngine(skills_dir="./skills")
    
    # Register custom tools
    for tool in DEFAULT_TOOLS:
        engine.register_tool(tool)
    
    # Agent will progressively load skills as needed
    task = """
I need to review this Python code for security issues:

```python
import sqlite3

def get_user(uid):
    conn = sqlite3.connect('users.db')
    return conn.execute(f'SELECT * FROM users WHERE id={uid}').fetchone()
```

Please use the Code Reviewer skill to perform a thorough security analysis.
"""
    
    response = engine.run(task)
    
    print("\n" + "="*60)
    print("FINAL RESPONSE:")
    print("="*60)
    print(response)

if __name__ == "__main__":
    main()
