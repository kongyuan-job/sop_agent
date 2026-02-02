"""Built-in tools for the Agent."""
import subprocess
import sys
from pathlib import Path
from langchain_core.tools import tool


@tool
def execute_python(code: str) -> str:
    """Execute Python code and return the output. Use this to run and test code."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        return output if output else "Code executed successfully with no output."
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out (30s limit)."
    except Exception as e:
        return f"Error executing code: {str(e)}"


@tool
def read_file(file_path: str) -> str:
    """Read the contents of a file. Use this to examine code or text files."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' not found."
        if not path.is_file():
            return f"Error: '{file_path}' is not a file."
        content = path.read_text(encoding="utf-8")
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def write_file(file_path: str, content: str) -> str:
    """Write content to a file. Creates the file if it doesn't exist."""
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} characters to '{file_path}'."
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool
def list_directory(directory_path: str = ".") -> str:
    """List contents of a directory. Use this to explore the file structure."""
    try:
        path = Path(directory_path)
        if not path.exists():
            return f"Error: Directory '{directory_path}' not found."
        if not path.is_dir():
            return f"Error: '{directory_path}' is not a directory."
        
        items = []
        for item in sorted(path.iterdir()):
            if item.is_dir():
                items.append(f"[DIR]  {item.name}/")
            else:
                items.append(f"[FILE] {item.name}")
        return "\n".join(items) if items else "Directory is empty."
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@tool
def search_in_files(directory: str, pattern: str) -> str:
    """Search for a pattern in files within a directory. Returns matching lines."""
    try:
        path = Path(directory)
        if not path.exists():
            return f"Error: Directory '{directory}' not found."
        
        results = []
        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".py", ".txt", ".md", ".json", ".yaml", ".yml"]:
                try:
                    content = file_path.read_text(encoding="utf-8")
                    for i, line in enumerate(content.split("\n"), 1):
                        if pattern.lower() in line.lower():
                            results.append(f"{file_path}:{i}: {line.strip()}")
                except:
                    continue
        
        return "\n".join(results[:50]) if results else f"No matches found for '{pattern}'."
    except Exception as e:
        return f"Error searching: {str(e)}"


# Export all tools
DEFAULT_TOOLS = [
    execute_python,
    read_file,
    write_file,
    list_directory,
    search_in_files,
]
