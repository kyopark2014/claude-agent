# Claude Agent

여기서는 [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)와 MCP를 이용하여 agent를 구현하고 활용하는 방법에 대해 설명합니다. 또한, AWS MCP인 use-aws, RAG를 위한 kb-retriever, code interpreter를 위한 repl-coder, AWS의 best practice를 조회할 수 있는 aws document와 같은 MCP 서버를 구현할 수 있습니다. Claude Agent SDK로 만든 agent는 코드 생성 뿐 아니라, multi turn으로 동작하므로 복잡한 작업에서 특히 좋은 성능을 보여줍니다. 

<img width="800" alt="image" src="https://github.com/user-attachments/assets/5acf2313-a156-4ab2-9eb8-55e68f167936" />

## Claude Agent SDK 

### Basic 

[claude_agent.py](./application/claude_agent.py)와 같이 Claude Agent SDK를 활용할 수 있습니다. 먼저 아래와 같이 SDK를 import 합니다. ClaudeAgentOptions을 이용해 Agent를 설정하고, 실행을 위해 query를 사용하고, streaming 결과에서 필요한 정보를 추출하기 위하여 AssistantMessage, SystemMessage, UserMessage, TextBlock을 이용합니다. 또한 debugging등의 목적으로 tool 결과를 ToolUseBlock, ToolResultBlock을 이용합니다.

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

### Session Management

이전 history를 session으로 관리할 수 있습니다. System message에서 아래와 같이 session-id를 가져올 수 있습니다.

```python
session-id = None
async for message in query(prompt=prompt, options=options):
    if isinstance(message, SystemMessage):
        subtype = message.subtype
        if subtype == "init":
            session_id = message.data.get('session_id')
            logger.info(f"Session started with ID: {session_id}")
```

이때의 session-id를 이용하여 agent에서 resume을 할 수 있습니다.

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

### AWS MCP: use-aws

[mcp_server_use_aws.py](./application/mcp_server_use_aws.py)에서는 아래와 같이 use_aws tool을 등록합니다. use_aws tool은 agent가 전달하는 service_name, operation_name, parameters를 받아서 실행하고 결과를 리턴합니다. service_name은 s3, ec2와 같은 서비스 명이며, operation_name은 list_buckets와 같은 AWS CLI 명령어 입니다. 또한, parameters는 이 명령어를 수행하는데 필요한 값입니다. 

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

[use-aws](./application/use_aws.py)은 [use_aws.py](https://github.com/strands-agents/tools/blob/main/src/strands_tools/use_aws.py)의 MCP 버전입니다. 



### 사용 준비 

아래와 같은 명령어로 credential을 설정합니다. 만약 AWS CLI가 설치되지 않았다면, [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)에 따라 설치후 credential을 설정합니다.

```text
aws configure
```

만약 workshop용 테스트 계정이라면 아래와 같이 설정합니다.

```python
aws configure set aws_access_key_id EXAMS3W4F4PXQPNBSBX1
aws configure set aws_secret_access_key 12345keypKY8+PjqMcIsd6ekBihuBZ8s108aLUB
aws configure set aws_session_token 12345JpZ2luX2VjENf//////////wEaCXVzLWVhc3QtMSJIMEYCIQClUKSzIECB0539JSN4aTrhexamplehr/YZeVU0OWiTMtXHwOXKpECCF8QAhoMMTY2ODkxNzM4MDk1IgznJKQqAdztbP5ZMFMq7gGJAxf9ktRKhcZgdZA2cmTzPoBzqQ+YbIJ2dnPkq+Hz33yUuMda5HAFedTtgq7RTTQbtFsJIJGQTwrsJ8akumUCuOjmzLpE1VUhiBqmO+nbrJk4Xhmxvi0c2hPx98eiDLdDfr6R1iCW4nZtUrQmMWsNS5LUDNtTWwVipuXTnNxs/y+AWa/ugsHQiUArsGuy54MYmZkIuXW9pbwxjAingPz5fKJedtI4J2P99NCL8dYlPaYlb0qXGoHT90k9ehjRKvbiAR9tk
```

[Claude Agent SDK for Python](https://github.com/anthropics/claude-agent-sdk-python)와 같이 Claude Code와 Claude Agent SDK를 설치합니다.

```text
npm install -g @anthropic-ai/claude-code

pip install claude-agent-sdk
```

<!--
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
-->

이제 아래와 같이 코드를 다운로드 합니다.

```text
git clone https://github.com/kyopark2014/claude-agent
cd claude-agent
```

이제 아래와 같이 agent를 실행합니다.

```python
streamlit run application/app.py
```

이때 아래와 같이 필요한 MCP 서버를 선택후 채팅창에 question을 넣고 실행할 수 있습니다.

<img width="400" alt="image" src="https://github.com/user-attachments/assets/21be21c9-c475-412d-a4b1-c63f81d6f1c3" />


### Permission

[ClaudeAgentOptions](https://docs.claude.com/en/api/agent-sdk/python#claudeagentoptions)에서 permission_mode를 설정할 때에 "default", "acceptEdits", "plan", "bypassPermissions"을 선택할 수 있습니다. 

- "plan": 모든 도구 사용에 대해 계획을 세우고 사용자 승인을 받습니다.
- "acceptEdits": 파일 편집 작업은 자동 승인, 다른 도구들은 권한 검사 적용합니다.
- "bypassPermissions": 모든 도구 사용을 자동 승인합니다.
- "default": 기본 권한 모드로 모든 도구에 대해 권한 프롬프트 표시합니다.

이때 설정을 "default"로 하고, weather tool을 이용하려고 하면 아래와 같은 에러를 받습니다.

```python
UserMessage(content=[ToolResultBlock(tool_use_id='toolu_bdrk_01RqbGiZUv1v2vK2fjLsaaGV', content="Claude requested permissions to use mcp__search__get_weather_info, but you haven't granted it yet.", is_error=True)], parent_tool_use_id=None)
```

여기서는 [Handling Permissions](https://docs.claude.com/en/api/agent-sdk/permissions)의 [canUseTool](https://docs.claude.com/en/api/agent-sdk/permissions#canusetool)을 이용항 auto approval을 적용합니다. 또한, 이때에는 [Streaming Input](https://docs.claude.com/en/api/agent-sdk/streaming-vs-single-mode)을 활용하여야 하며, 아래와 구현 할 수 있습니다.

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

사용할 수 있는 모델의 확인 방법은 아래와 같습니다.

```text
aws bedrock list-foundation-models --region=us-west-2 --by-provider anthropic --query "modelSummaries[*].modelId"
```

날씨와 인터넷 검색은 secreat manager에 key 등록이 필요합니다. [Console-SecretManage](https://us-west-2.console.aws.amazon.com/secretsmanager/listsecrets?region=us-west-2)에서 생성한 API에 대한 Credential을 입력합니다.

<img width="545" height="199" alt="image" src="https://github.com/user-attachments/assets/98f3592a-a69d-440e-8318-31f5f7efe128" />

- 날씨 검색: [openweathermap](https://home.openweathermap.org/api_keys)에 접속하여 API Key를 발급합니다.
- 인터넷 검색: [Tavily Search](https://app.tavily.com/sign-in)에 접속하여 가입 후 API Key를 발급합니다. 이것은 tvly-로 시작합니다.  

날씨는 "basic" MCP를 선택한 후에 아래와 같이 도시 이름을 이용해 조회합니다.

<img width="653" height="369" alt="image" src="https://github.com/user-attachments/assets/f7fccb0c-8492-421e-96ed-bc8fd4ad6902" />

인터넷 검색은 "tavily-search" MCP를 선택한 후에 아래와 같이 검색합니다.

<img width="652" height="673" alt="image" src="https://github.com/user-attachments/assets/62a02161-dbab-45db-bb1f-783317c09cc4" />




## 실행 결과

아래와 같이 EKS의 상태를 분석하는 리포트 생성을 요청하면, use-aws tool을 이용하여 AWS의 각종 리소스를 조회하고 요약하여 리포트를 작성할 수 있습니다.

<img width="728" height="753" alt="image" src="https://github.com/user-attachments/assets/85cc59a6-8664-4d01-b506-036b5b561178" />




## Reference 

[Agent SDK overview](https://docs.claude.com/en/api/agent-sdk/overview)

[Claude Agent SDK for Python](https://github.com/anthropics/claude-agent-sdk-python)

[Amazon Bedrock에서 Claude Code](https://docs.claude.com/ko/docs/claude-code/amazon-bedrock)

[Claude Code 설정](https://docs.claude.com/ko/docs/claude-code/settings)

[System Prompts](https://docs.claude.com/en/release-notes/system-prompts#september-29-2025)

[Claude Code 소개](https://www.linkedin.com/posts/gb-jeong_lg-ai-%EB%A6%AC%EC%84%9C%EC%B9%98%EC%97%90%EC%84%9C-claude-code-%EC%84%B8%EB%AF%B8%EB%82%98%EB%A5%BC-%ED%96%88%EC%8A%B5%EB%8B%88%EB%8B%A4-%EB%91%90-%EC%8B%9C%EA%B0%84-%EC%84%B8%EB%AF%B8%EB%82%98-activity-7379535599906693121-3cM4/?utm_source=share&utm_medium=member_android&rcm=ACoAAA5jTp0BX-JuOkof3Ak56U3VlXjQVT43NzQ)

[Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

[Streaming Input](https://docs.claude.com/en/api/agent-sdk/streaming-vs-single-mode)

