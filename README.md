# Claude Agent

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

<img width="728" height="753" alt="image" src="https://github.com/user-attachments/assets/85cc59a6-8664-4d01-b506-036b5b561178" />




## Reference 

[Claude Agent SDK for Python](https://github.com/anthropics/claude-agent-sdk-python)

[Amazon Bedrock에서 Claude Code](https://docs.claude.com/ko/docs/claude-code/amazon-bedrock)

[Claude Code 설정](https://docs.claude.com/ko/docs/claude-code/settings)

