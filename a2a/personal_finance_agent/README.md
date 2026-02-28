# Personal Finance Agent

## Introduction

A specialized A2A agent for personal finance analysis that connects to the Personal Finance MCP tool to provide insights about your financial data. The agent dynamically loads tools from the connected MCP server and uses an LLM to orchestrate tool calls for analyzing transactions, accounts, spending patterns, and budgets.

## Features

- **Multi-MCP Support**: Connect to multiple MCP servers simultaneously
- **Dynamic Tool Loading**: Automatically discovers and uses tools from connected MCP servers
- **LLM Agnostic**: Works with any OpenAI-compatible API (Ollama, OpenAI, etc.)
- **A2A Protocol**: Full integration with A2A server for task management and streaming

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_URLS` | Comma-separated list of MCP server URLs | `http://localhost:8000/mcp` |
| `MCP_TRANSPORT` | Transport protocol for MCP | `streamable_http` |
| `LLM_MODEL` | Model name to use | `llama3.2:3b-instruct-fp16` |
| `LLM_API_BASE` | Base URL for LLM API | `http://localhost:11434/v1` |
| `LLM_API_KEY` | API key for LLM service | `dummy` |

### MCP Configuration

The agent can be configured with single or multiple MCP servers via the `MCP_URLS` environment variable:

```bash
# Required
MCP_URLS="http://weather-tool:8000/mcp" # Single MCP Server
MCP_URLS="http://weather-tool:8000/mcp,http://movie-tool:8000/mcp" # Multiple MCP servers
```

### Usage Example

Once deployed, the agent can handle requests like:
```
"How much did I spend on restaurants last year?"
"Show me my account balances"
"What were my top expenses last month?"
"How much did I spend on travel last year?"
"Show me my top 10 merchants"
```

The agent automatically selects the appropriate tool from the Personal Finance MCP server and returns formatted results with financial insights. 

## Running in Kagenti

When deploying in the Kagenti UI:

1. Import your intended tools using the `Import New Tools` section.
2. In the `Import New Agent` section, follow the given prompts and configure these environmental variables:
  - Choose the `ollama` or `openai` environmental variable set
  - Create a new variable, `MCP_URLS`, and add your list of MCP server URLs separated with commas.