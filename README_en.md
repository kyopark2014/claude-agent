# Claude Agent

This document explains how to implement and utilize agents using the [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) and MCP. You can implement MCP servers such as use-aws (an AWS MCP), kb-retriever (for RAG), repl-coder (for code interpreter), and aws document (which can query AWS best practices). Agents built with Claude Agent SDK show particularly good performance in complex tasks as well as code generation by utilizing the [feedback loop](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk).

<img width="800" alt="image" src="https://github.com/user-attachments/assets/5acf2313-a156-4ab2-9eb8-55e68f167936" />

## Claude Agent SDK

### Basic

You can utilize the Claude Agent SDK as shown in [claude_agent.py](./application/claude_agent.py). First, import the SDK as shown below. Use ClaudeAgentOptions to configure the Agent, use query for execution, and use AssistantMessage, SystemMessage, UserMessage, TextBlock to extract necessary information from streaming results. Also use ToolUseBlock, ToolResultBlock for tool results for debugging purposes.

```python
from claude_agent_sdk import (
    query,
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,    
    SystemMessage,
    UserMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    ToolPermissionContext,
    PermissionResultAllow,
    PermissionResultDeny
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
        "Provide sufficient specific details for the situation."
        "If you don't know the answer, say you don't know."
        "Answer in Korean."
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
async with ClaudeSDKClient(options=options) as client:
    await client.query(prompt)

    async for message in client.receive_response():
        if isinstance(message, SystemMessage):
            subtype = message.subtype
            data = message.data
            if subtype == "init":
                session_id = message.data.get('session_id')
            if "tools" in data:
                tools = data["tools"]
                add_notification(containers, f"Tools: {tools}")
        elif isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    add_system_message(containers, f"{block.text}", "markdown")
                    final_result = block.text
                elif isinstance(block, ToolUseBlock):
                    add_notification(containers, f"Tool name: {block.name}, input: {block.input}")
                elif isinstance(block, ToolResultBlock):
                    add_notification(containers, f"Tool result: {block.content}")                
        elif isinstance(message, UserMessage):
            for block in message.content:
                if isinstance(block, ToolResultBlock):
                    add_notification(containers, f"Tool result: {block.content}")                    
                    if isinstance(block.content, list):
                        for item in block.content:
                            if isinstance(item, dict) and "text" in item:
                                if "path" in item['text']:
                                    json_path = json.loads(item['text'])
                                    path = json_path.get('path', "")
                                    image_url.append(path)
```

### Session Management

Previous history can be managed as a session. You can get the session-id from the System message as shown below.

```python
session-id = None
async for message in query(prompt=prompt, options=options):
    if isinstance(message, SystemMessage):
        subtype = message.subtype
        if subtype == "init":
            session_id = message.data.get('session_id')
            logger.info(f"Session started with ID: {session_id}")
```

You can resume the agent using this session-id.

```python
options = ClaudeAgentOptions(
    system_prompt=system,
    max_turns=100,
    permission_mode="bypassPermissions",
    model=get_model_id(),
    mcp_servers=server_params,
    resume=session_id
)
```

### Utilizing CLAUDE.md

Claude agent automatically loads [CLAUDE.md](https://www.anthropic.com/engineering/claude-code-best-practices) and places it at the top of the context, making it useful for repeatedly applying prompts. When utilizing CLAUDE.md in Claude Agent SDK, select the appropriate path using setting_sources as shown below.

```python
options = ClaudeAgentOptions(
    system_prompt=system,
    max_turns=100,
    permission_mode="default", 
    model=get_model_id(),
    mcp_servers=server_params,
    can_use_tool=prompt_for_tool_approval,
    setting_sources=["project"]
)
```

### AWS MCP: use-aws

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

### Setup Preparation

Set up credentials with the following commands. If AWS CLI is not installed, install it according to [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and then set up credentials.

```text
aws configure
```

If it's a test account for workshops, set it up as follows.

```python
aws configure set aws_access_key_id EXAMS3W4F4PXQPNBSBX1
aws configure set aws_secret_access_key 12345keypKY8+PjqMcIsd6ekBihuBZ8s108aLUB
aws configure set aws_session_token 12345JpZ2luX2VjENf//////////wEaCXVzLWVhc3QtMSJIMEYCIQClUKSzIECB0539JSN4aTrhexamplehr/YZeVU0OWiTMtXHwOXKpECCF8QAhoMMTY2ODkxNzM4MDk1IgznJKQqAdztbP5ZMFMq7gGJAxf9ktRKhcZgdZA2cmTzPoBzqQ+YbIJ2dnPkq+Hz33yUuMda5HAFedTtgq7RTTQbtFsJIJGQTwrsJ8akumUCuOjmzLpE1VUhiBqmO+nbrJk4Xhmxvi0c2hPx98eiDLdDfr6R1iCW4nZtUrQmMWsNS5LUDNtTWwVipuXTnNxs/y+AWa/ugsHQiUArsGuy54MYmZkIuXW9pbwxjAingPz5fKJedtI4J2P99NCL8dYlPaYlb0qXGoHT90k9ehjRKvbiAR9tk
```

## Setup

Install Claude Code and Claude Agent SDK as shown in [Claude Agent SDK for Python](https://github.com/anthropics/claude-agent-sdk-python).

```text
npm install -g @anthropic-ai/claude-code

pip install claude-agent-sdk
```

<!--
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
-->

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


### Permission

When setting permission_mode in [ClaudeAgentOptions](https://docs.claude.com/en/api/agent-sdk/python#claudeagentoptions), you can choose from "default", "acceptEdits", "plan", and "bypassPermissions".

- "plan": Plans all tool uses and gets user approval.
- "acceptEdits": Auto-approves file editing operations, applies permission checks to other tools.
- "bypassPermissions": Auto-approves all tool uses.
- "default": Default permission mode that shows permission prompts for all tools.

If you set it to "default" and try to use the weather tool, you will receive the following error:

```python
UserMessage(content=[ToolResultBlock(tool_use_id='toolu_bdrk_01RqbGiZUv1v2vK2fjLsaaGV', content="Claude requested permissions to use mcp__search__get_weather_info, but you haven't granted it yet.", is_error=True)], parent_tool_use_id=None)
```

Therefore, we apply auto approval using [canUseTool](https://docs.claude.com/en/api/agent-sdk/permissions#canusetool) from [Handling Permissions](https://docs.claude.com/en/api/agent-sdk/permissions). We can also implement it using [Streaming Input](https://docs.claude.com/en/api/agent-sdk/streaming-vs-single-mode) as shown below.

```python
async def prompt_for_tool_approval(tool_name: str, input_params: dict, context: ToolPermissionContext):
    result = PermissionResultAllow(updated_input=input_params)

options = ClaudeAgentOptions(
    system_prompt=system,
    max_turns=100,
    permission_mode="default", 
    model=get_model_id(),
    mcp_servers=server_params,
    can_use_tool=prompt_for_tool_approval
)
async with ClaudeSDKClient(options=options) as client:
    await client.query(prompt)
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                logger.info(f"--> TextBlock: {block.text}")
```            


### Tips

The method to check available models is as follows.

```text
aws bedrock list-foundation-models --region=us-west-2 --by-provider anthropic --query "modelSummaries[*].modelId"
```

Weather and internet search require API key registration in Secret Manager. Enter the credentials for the created API in [Console-SecretManage](https://us-west-2.console.aws.amazon.com/secretsmanager/listsecrets?region=us-west-2).

<img width="545" height="199" alt="image" src="https://github.com/user-attachments/assets/98f3592a-a69d-440e-8318-31f5f7efe128" />

- Weather search: Access [openweathermap](https://home.openweathermap.org/api_keys) to get an API Key.
- Internet search: Access [Tavily Search](https://app.tavily.com/sign-in), sign up, and get an API Key. It starts with tvly-.

For weather, select the "basic" MCP and query using the city name as shown below.

<img width="653" height="369" alt="image" src="https://github.com/user-attachments/assets/f7fccb0c-8492-421e-96ed-bc8fd4ad6902" />

For internet search, select the "tavily-search" MCP and search as shown below.

<img width="652" height="673" alt="image" src="https://github.com/user-attachments/assets/62a02161-dbab-45db-bb1f-783317c09cc4" />




## Execution Results

When you request generation of a report analyzing EKS status as shown below, you can query various AWS resources using the use-aws tool and create a report by summarizing them.

<img width="728" height="753" alt="image" src="https://github.com/user-attachments/assets/85cc59a6-8664-4d01-b506-036b5b561178" />



## Reference 

[Agent SDK overview](https://docs.claude.com/en/api/agent-sdk/overview)

[Claude Agent SDK for Python](https://github.com/anthropics/claude-agent-sdk-python)

[Claude Code on Amazon Bedrock](https://docs.claude.com/ko/docs/claude-code/amazon-bedrock)

[Claude Code Settings](https://docs.claude.com/ko/docs/claude-code/settings)

[System Prompts](https://docs.claude.com/en/release-notes/system-prompts#september-29-2025)

[Claude Code Introduction](https://www.linkedin.com/posts/gb-jeong_lg-ai-%EB%A6%AC%EC%84%9C%EC%B9%98%EC%97%90%EC%84%9C-claude-code-%EC%84%B8%EB%AF%B8%EB%82%98%EB%A5%BC-%ED%96%88%EC%8A%B5%EB%8B%88%EB%8B%A4-%EB%91%90-%EC%8B%9C%EA%B0%84-%EC%84%B8%EB%AF%B8%EB%82%98-activity-7379535599906693121-3cM4/?utm_source=share&utm_medium=member_android&rcm=ACoAAA5jTp0BX-JuOkof3Ak56U3VlXjQVT43NzQ)

[Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

[Streaming Input](https://docs.claude.com/en/api/agent-sdk/streaming-vs-single-mode)

