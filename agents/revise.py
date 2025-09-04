#from agents.prompts import revision_prompt
import os
from anthropic import Anthropic

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

class RevisionAgent:
    def __init__(self, system_prompt):
        self.client = Anthropic(api_key = os.environ["anthropic_api_key"])
        self.system_prompt = system_prompt

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def revise_content(self, content: str, user_feedback: str):
        system = self.system_prompt

        Prompt = f"""
        Please revise and adapt the content based on the user feedback provided below:
        Content: --{content}--
        User feedback: --{user_feedback}--
        """

        message = self.client.messages.create(
                model="claude-3-7-sonnet-latest",
                max_tokens=4096,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 2048
                },
                system=self.system_prompt,
                messages=[
                        {"role": "user", "content": Prompt}
                    ])
        return message.content[-1].text
