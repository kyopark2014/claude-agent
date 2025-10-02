# Claude Agent

여기서는 [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)와 MCP를 이용하여 Agent를 생성하여 활용하는 방법에 대해 설명합니다.

## Claude Agent SDK

[claude_agent.py](./application/claude_agent.py)와 같이 Claude Agent SDK를 활용할 수 있습니다. 먼저 아래와 같이 SDK를 import 합니다. ClaudeAgentOptions을 이용해 Agent를 설정하고, 실행을 위해 query를 사용하고, streaming 결과에서 필요한 정보를 추출하기 위하여 AssistantMessage, SystemMessage, UserMessage, TextBlock을 이용합니다. 또한 debugging등의 목적으로 tool 결과를 ToolUseBlock, ToolResultBlock을 이용합니다.

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

여기서는 Streamlit 메뉴에서 MCP를 선택하여 이용합니다. 이를 위해 아래와 같이 mcp_server에 대한 정보를 가지고 MCP server 정보를 생성합니다.

```python
mcp_json = mcp_config.load_selected_config(mcp_servers)
server_params = load_multiple_mcp_server_parameters(mcp_json)
```

생성된 서버의 정보는 아래와 같은 json 형태입니다.

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

이제 아래와 같이 용도에 맞게 system prompt를 준비하고 [ClaudeAgentOptions](https://github.com/anthropics/claude-agent-sdk-python?tab=readme-ov-file#using-tools)을 정의합니다. 이때, 최대 turn의 숫자, 사용자 확인의 bypass 여부, 모델 ID, 서버 정보를 설정합니다. 

```python
if isKorean(prompt):
    system = (
        "당신의 이름은 서연이고, 질문에 친근한 방식으로 대답하도록 설계된 대화형 AI입니다."
        "상황에 맞는 구체적인 세부 정보를 충분히 제공합니다."
        "모르는 질문을 받으면 솔직히 모른다고 말합니다."
        "한국어로 답변하세요."
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

Agent에 요청을 query를 이용해 요청하면, prompt에 있는 사용자 요청에 대한 응답을 stream으로 얻을 수 있습니다. 이때 첫번째 응답는 SystemMessage이며 아래와 같이 Agent에서 사용할 수 있는 tool에 대한 정보를 가지고 있습니다. 또한 Assistant Message에서 TextBlock을 추출하면 Agent의 결과를 활용할 수 있습니다. 또한 ToolUseBlock에서 사용된 tool에 대한 정보를 얻고, User Message의 ToolResultBlock에서 tool의 실행 결과를 확인할 수 있습니다.

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

## 사용준비 

[Claude Agent SDK for Python](https://github.com/anthropics/claude-agent-sdk-python)와 같이 Claude Code와 Claude Agent SDK를 설치합니다.

```text
npm install -g @anthropic-ai/claude-code

pip install claude-agent-sdk
```

[Claude Code 설정](https://docs.claude.com/ko/docs/claude-code/settings)와 같이 사용자 설정을 위한 ~/.claude/settings.json 을 생성합니다. 만약 AWS CLI의 refresh가 필요하다면, [Bedrock 인증](https://docs.claude.com/ko/api/agent-sdk/overview#%EC%9D%B8%EC%A6%9D)을 참조하여 설정합니다.

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


또는 아래와 같이 환경변수를 설정할 수 있습니다.

```text
export CLAUDE_CODE_USE_BEDROCK=1
export ANTHROPIC_MODEL='us.anthropic.claude-sonnet-4-5-20250929-v1:0'
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=4096
```

## 실행 결과

아래와 같이 EKS의 상태를 분석하는 리포트 생성을 요청하면, use-aws tool을 이용하여 AWS의 각종 리소스를 조회하고 요약하여 리포트를 작성할 수 있습니다.

<img width="728" height="753" alt="image" src="https://github.com/user-attachments/assets/85cc59a6-8664-4d01-b506-036b5b561178" />




## Reference 

[Claude Agent SDK for Python](https://github.com/anthropics/claude-agent-sdk-python)

[Amazon Bedrock에서 Claude Code](https://docs.claude.com/ko/docs/claude-code/amazon-bedrock)

[Claude Code 설정](https://docs.claude.com/ko/docs/claude-code/settings)

