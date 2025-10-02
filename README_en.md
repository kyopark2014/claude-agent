# Claude Agent

This document explains how to implement and utilize agents using the [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) and MCP. Here, the agent has MCP servers such as use-aws (an AWS MCP), kb-retriever (for RAG), repl-coder (for code interpreter), and aws document (which can query AWS best practices). Using MCP, you can retrieve necessary information or perform required tasks. Claude Agent operates in multi-turn mode, showing particularly good performance in complex tasks.

<img width="800" alt="image" src="https://github.com/user-attachments/assets/5acf2313-a156-4ab2-9eb8-55e68f167936" />

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

## AWS MCP: use-aws

In [mcp_server_use_aws.py](./application/mcp_server_use_aws.py), the `use_aws` tool is registered as shown below. The `use_aws` tool receives `service_name`, `operation_name`, and `parameters` from the agent, executes the request, and returns the result. `service_name` is the AWS service name such as S3 or EC2, and `operation_name` is an AWS SDK/CLI operation such as `list_buckets`. `parameters` are the arguments required to run the operation.

```python
import use_aws as aws_utils

@mcp.tool()
def use_aws(service_name, operation_name, parameters, region, label, profile_name) -> Dict[str, Any]:
    console = aws_utils.create()
    available_operations = get_available_operations(service_name)

    client = get_boto3_client(service_name, region, profile_name)
    operation_method = getattr(client, operation_name)

    response = operation_method(**parameters)
    for key, value in response.items():
        if isinstance(value, StreamingBody):
            content = value.read()
            try:
                response[key] = json.loads(content.decode("utf-8"))
            except json.JSONDecodeError:
                response[key] = content.decode("utf-8")
    return {
        "status": "success",
        "content": [{"text": f"Success: {str(response)}"}],
    }
```

[use-aws](./application/use_aws.py) is the MCP version of [`use_aws.py`](https://github.com/strands-agents/tools/blob/main/src/strands_tools/use_aws.py).



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

Now download the code as follows.

```text
git clone https://github.com/kyopark2014/claude-agent
cd claude-agent
```

Now run the agent as follows.

```python
streamlit run application/app.py
```

At this point, select the required MCP servers as shown below, enter your question in the chat, and run.

<img width="400" alt="image" src="https://github.com/user-attachments/assets/21be21c9-c475-412d-a4b1-c63f81d6f1c3" />



## Execution Results

When you request generation of a report analyzing EKS status as shown below, you can query various AWS resources using the use-aws tool and create a report by summarizing them.


<img width="655" height="814" alt="image" src="https://github.com/user-attachments/assets/76e9365f-3d78-43ec-a05a-6b5f5981ea67" />



## Reference 

[Claude Agent SDK for Python](https://github.com/anthropics/claude-agent-sdk-python)

[Claude Code on Amazon Bedrock](https://docs.claude.com/ko/docs/claude-code/amazon-bedrock)

[Claude Code Settings](https://docs.claude.com/ko/docs/claude-code/settings)

