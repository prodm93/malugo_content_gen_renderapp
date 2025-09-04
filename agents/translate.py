import os
from anthropic import Anthropic
from agents.prompts import translation_prompt
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

class TranslationAgent:
    def __init__(self):
        self.client = Anthropic(api_key = os.environ["anthropic_api_key"])

    #@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def translate(self, content:str):
        Prompt = f"""
        Please translate the content provided below to Brazilian Portuguese:
        Content: --{content}--
        """

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            thinking={
                "type": "enabled",
                "budget_tokens": 2048
            },
            system=translation_prompt,
            messages=[
                    {"role": "user", "content": Prompt}
                ])
        return message.content[-1].text



