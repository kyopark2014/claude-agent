# Claude Agent

This document explains how to create and utilize an Agent using [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) and MCP.

## Claude Agent SDK

You can utilize the Claude Agent SDK as shown in [claude_agent.py](./application/claude_agent.py). First, import the SDK as shown below. Use ClaudeAgentOptions to configure the Agent, use query for execution, and use AssistantMessage, SystemMessage, UserMessage, TextBlock to extract necessary information from streaming results. Also use ToolUseBlock, ToolResultBlock for tool results for debugging purposes.

```python
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,    
    SystemMessage,
    UserMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock    
)
```

Here, we use MCP by selecting it from the Streamlit menu. For this purpose, we generate MCP server information with information about mcp_server as shown below.

```python
mcp_json = mcp_config.load_selected_config(mcp_servers)
server_params = load_multiple_mcp_server_parameters(mcp_json)
```

The generated server information is in the following JSON format.

```java
{
   "search":{
      "transport":"stdio",
      "command":"python",
      "args":[
         "/Users/claude-agent/application/mcp_server_basic.py"
      ],
      "env":{
         
      }
   },
   "use-aws":{
      "transport":"stdio",
      "command":"python",
      "args":[
         "/Users/claude-agent/application/mcp_server_use_aws.py"
      ],
      "env":{
         
      }
   }
}
```

Now, prepare a system prompt suitable for the purpose as shown below and define [ClaudeAgentOptions](https://github.com/anthropics/claude-agent-sdk-python?tab=readme-ov-file#using-tools). At this time, set the maximum number of turns, user confirmation bypass, model ID, and server information. 

```python
if isKorean(prompt):
    system = (
        "Your name is Seoyeon, and you are a conversational AI designed to answer questions in a friendly manner."
        "Provide sufficient specific details appropriate for the situation."
        "If you don't know the answer to a question, honestly say you don't know."
        "Please respond in Korean."
    )
else:
    system = (
        "You are a helpful assistant"
        "Provide sufficient specific details for the situation."
        "If you don't know the answer, say you don't know."
    )

options = ClaudeAgentOptions(
    system_prompt=system,
    max_turns=100,
    permission_mode="bypassPermissions",
    model=get_model_id(),
    mcp_servers=server_params
)
```

When you make a request to the Agent using query, you can get a stream response to the user request in the prompt. At this time, the first response is a SystemMessage that contains information about tools available to the Agent as shown below. You can also extract TextBlock from Assistant Message to utilize the Agent's results. You can also get information about tools used in ToolUseBlock and check tool execution results in ToolResultBlock of User Message.

```python
final_result = ""    
async for message in query(prompt=prompt, options=options):
    if isinstance(message, SystemMessage):
        data = message.data
        if "tools" in data:
            tools = data["tools"]
            add_notification(containers, f"Tools: {tools}")

    elif isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                add_notification(containers, f"{block.text}")
                final_result = block.text

    elif isinstance(block, ToolUseBlock):
        add_notification(containers, f"Tool name: {block.name}, input: {block.input}")

    elif isinstance(message, UserMessage):
        for block in message.content:
            if isinstance(block, ToolResultBlock):
                add_notification(containers, f"Tool result: {block.content}")                
```

## Setup

Install Claude Code and Claude Agent SDK as shown in [Claude Agent SDK for Python](https://github.com/anthropics/claude-agent-sdk-python).

```text
npm install -g @anthropic-ai/claude-code

pip install claude-agent-sdk
```

Create ~/.claude/settings.json for user settings as shown in [Claude Code Settings](https://docs.claude.com/ko/docs/claude-code/settings). If AWS CLI refresh is needed, refer to [Bedrock Authentication](https://docs.claude.com/ko/api/agent-sdk/overview#%EC%9D%B8%EC%A6%9D) for configuration.

```java
{
    "awsAuthRefresh": "aws sso login --profile default",
    "env": {
      "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
      "OTEL_METRICS_EXPORTER": "otlp",
      "AWS_PROFILE": "default",
      "CLAUDE_CODE_USE_BEDROCK": "1"
    }
}
```


Alternatively, you can set environment variables as shown below.

```text
export CLAUDE_CODE_USE_BEDROCK=1
export ANTHROPIC_MODEL='us.anthropic.claude-sonnet-4-5-20250929-v1:0'
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=4096
```

## Execution Results

When you request generation of a report analyzing EKS status as shown below, you can query various AWS resources using the use-aws tool and create a report by summarizing them.

<img width="728" height="753" alt="image" src="https://github.com/user-attachments/assets/85cc59a6-8664-4d01-b506-036b5b561178" />




## Reference 

[Claude Agent SDK for Python](https://github.com/anthropics/claude-agent-sdk-python)

[Claude Code on Amazon Bedrock](https://docs.claude.com/ko/docs/claude-code/amazon-bedrock)

[Claude Code Settings](https://docs.claude.com/ko/docs/claude-code/settings)

