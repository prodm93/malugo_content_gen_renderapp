from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

class QALegalComplianceAgent:
    def __init__(self, sys_prompt):
        self.client = OpenAI()
        self.MODEL = "o4-mini"
        self.sys_prompt = sys_prompt

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def suggest_revisions(self, content: str, qa_standards: str, legal_guidelines: str):
        system = self.sys_prompt
        
        user = f"""
        Please suggest content for the specified idea and content type:
        Content: --{content}--
        Quality assurance standards: --{qa_standards}--
        Legal compliance guidelines: --{legal_guidelines}--
        """

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        response = self.client.chat.completions.create(
            model=self.MODEL,
            reasoning_effort="medium",
            messages=messages,
            #temperature=0.7
        )

        return response.choices[0].message.content
