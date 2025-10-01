# Basic 동작

아래와 같이 hello_world를 실행합니다.

```text
python hello_world.py
```

이때의 결과는 아래와 같습니다.

```text
hello_world.py:19 | SystemMessage(subtype='init', data={'type': 'system', 'subtype': 'init', 'cwd': '/Users/ksdyb/Documents/src/claude-agent', 'session_id': '397f232e-5159-41a5-9d6f-efcf2b6e0223', 'tools': ['Task', 'Bash', 'Glob', 'Grep', 'ExitPlanMode', 'Read', 'Edit', 'Write', 'NotebookEdit', 'WebFetch', 'TodoWrite', 'BashOutput', 'KillShell', 'SlashCommand'], 'mcp_servers': [], 'model': 'us.anthropic.claude-sonnet-4-5-20250929-v1:0', 'permissionMode': 'default', 'slash_commands': ['compact', 'context', 'cost', 'init', 'output-style:new', 'pr-comments', 'release-notes', 'todos', 'review', 'security-review'], 'apiKeySource': 'none', 'output_style': 'default', 'agents': ['general-purpose', 'statusline-setup', 'output-style-setup'], 'uuid': 'abde20a3-f68f-4902-a40b-1eaec1999d84'})
hello_world.py:19 | AssistantMessage(content=[TextBlock(text='4')], model='claude-sonnet-4-5-20250929', parent_tool_use_id=None)
hello_world.py:19 | ResultMessage(subtype='success', duration_ms=4805, duration_api_ms=7220, is_error=False, num_turns=1, session_id='397f232e-5159-41a5-9d6f-efcf2b6e0223', total_cost_usd=0.004595, usage={'input_tokens': 4, 'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 14192, 'output_tokens': 5, 'server_tool_use': {'web_search_requests': 0}, 'service_tier': 'standard', 'cache_creation': {'ephemeral_1h_input_tokens': 0, 'ephemeral_5m_input_tokens': 0}}, result='4')
```

여기서 system message는 아래와 같습니다. 

```java
{
   "type":"system",
   "subtype":"init",
   "cwd":"/Users/ksdyb/Documents/src/claude-agent",
   "session_id":"397f232e-5159-41a5-9d6f-efcf2b6e0223",
   "tools":[
      "Task",
      "Bash",
      "Glob",
      "Grep",
      "ExitPlanMode",
      "Read",
      "Edit",
      "Write",
      "NotebookEdit",
      "WebFetch",
      "TodoWrite",
      "BashOutput",
      "KillShell",
      "SlashCommand"
   ],
   "mcp_servers":[
      
   ],
   "model":"us.anthropic.claude-sonnet-4-5-20250929-v1:0",
   "permissionMode":"default",
   "slash_commands":[
      "compact",
      "context",
      "cost",
      "init",
      "output-style:new",
      "pr-comments",
      "release-notes",
      "todos",
      "review",
      "security-review"
   ],
   "apiKeySource":"none",
   "output_style":"default",
   "agents":[
      "general-purpose",
      "statusline-setup",
      "output-style-setup"
   ],
   "uuid":"abde20a3-f68f-4902-a40b-1eaec1999d84"
}
```

AssistantMessage의 content로 결과를 확인할 수 있습니다.

```java
[TextBlock(text='4')]
```

ResultMessage로 실행 시간, 사용 토큰등 각종 실행 정보를 확인합니다.



