import subprocess
import json
from config import client, GEMINI_MODEL
from google.genai import types

def run_command(command: str) -> str:
    """Run a shell command on the user's computer"""
    result = subprocess.run(
        command, shell=True,
        capture_output=True, text=True, timeout=30
    )
    return result.stdout + result.stderr

def read_file(path: str) -> str:
    """Read a file from the filesystem"""
    with open(path, "r") as f:
        return f.read()

def write_file(path: str, content: str) -> str:
    """Write content to a file"""
    with open(path, "w") as f:
        f.write(content)
    return f"Wrote to {path}"

def web_search(query: str) -> str:
    """Search the web for information"""
    return f"Search results for: {query}"

TOOLS_FUNCTIONS = [run_command, read_file, write_file, web_search]

def execute_tool(name, args):
    if name == "run_command":
        return run_command(args["command"])
    elif name == "read_file":
        return read_file(args["path"])
    elif name == "write_file":
        return write_file(args["path"], args["content"])
    elif name == "web_search":
        return web_search(args["query"])
    return f"Unknown tool: {name}"

def run_agent_turn(messages, system_prompt):
    """Run one full agent turn using Gemini tool use."""
    while True:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=messages,
            config={
                'tools': TOOLS_FUNCTIONS,
                'system_instruction': system_prompt
            }
        )
        
        # Add assistant response content to history (including potential tool calls)
        assistant_content = response.candidates[0].content
        messages.append(assistant_content)
        
        # Identify function calls in the last response
        function_calls = [p.function_call for p in assistant_content.parts if p.function_call]
        
        if not function_calls:
            return response.text, messages
            
        # Execute all function calls and gather responses
        tool_responses = []
        for call in function_calls:
            print(f"  Tool: {call.name}({json.dumps(call.args)})")
            result = execute_tool(call.name, call.args)
            tool_responses.append(types.Part.from_function_response(
                name=call.name,
                response={'result': result}
            ))
            
        # Add tool response content to history
        messages.append(types.Content(role="user", parts=tool_responses))