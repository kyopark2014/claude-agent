import anyio
from claude_agent_sdk import query
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock

import logging
import sys
logging.basicConfig(
    level=logging.INFO,  # Default to INFO level
    format='%(filename)s:%(lineno)d | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("hello_world")

prompt = "서울에서 제주 여행 계획을 짜줘"

options = ClaudeAgentOptions(
    system_prompt="You are a helpful assistant",
    max_turns=1
)

async def main():
    async for message in query(prompt=prompt, options=options):
        logger.info(message)

        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    logger.info(block.text)

anyio.run(main)