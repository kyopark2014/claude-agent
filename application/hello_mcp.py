import anyio
from claude_agent_sdk import query
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, UserMessage, TextBlock, ToolResultBlock, ToolUseBlock

import logging
import sys
logging.basicConfig(
    level=logging.INFO,  # Default to INFO level
    format='%(filename)s:%(lineno)d | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("hello_mcp")


prompt = "내 S3 bucket 사용 현황은?"

options = ClaudeAgentOptions(
    system_prompt="You are a helpful assistant",
    max_turns=100,
    permission_mode="bypassPermissions",
    mcp_servers={
        "use_aws": {
            "type": "stdio",
            "command": "python",
            "args": ["-m", "mcp_server_use_aws"]
        }
    }
)

async def main():
    async for message in query(prompt=prompt, options=options):
        # logger.info(message)

        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    logger.info(f"--> TextBlock: {block.text}")
                elif isinstance(block, ToolUseBlock):
                    logger.info(f"tool_use_id: {block.id=}, name: {block.name}, input: {block.input}")
                elif isinstance(block, ToolResultBlock):
                    logger.info(f"tool_use_id: {block.tool_use_id=}, content: {block.content}")
                else:
                    logger.info(f"AssistantMessage: {block}")
                
        elif isinstance(message, UserMessage):
            for block in message.content:
                if isinstance(block, ToolResultBlock):
                    logger.info(f"tool_use_id: {block.tool_use_id=}, content: {block.content}")
                    
                    if isinstance(block.content, list):
                        for item in block.content:
                            if isinstance(item, dict) and "text" in item:
                                logger.info(f"--> ToolResult: {item['text']}")
                else:
                    logger.info(f"UserMessage: {block}")
        else:
            logger.info(f"Message: {message}")

anyio.run(main)