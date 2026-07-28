# lewm-mcp (MCPB Bundle)

FastMCP 3.2 server for LeWorldModel (LeWM): JEPA train/infer, planning hooks, agentic prep, fleet webapp

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "lewm-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "lewm_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **lewm_world**: lewm_world

## Requirements

- Python 3.12+
- uv
