
import os
from agents.translate import TranslationAgent
from agents.idea import IdeaAgent as _IdeaAgent
from agents.content import UnifiedGenAgent as _UnifiedGenAgent
from agents.revise import RevisionAgent
from agents.compliance import QALegalComplianceAgent
from agents.prompts import idea_prompt_openai, content_prompt, translation_prompt

class TranslateAgent:
    def __init__(self, system_prompt: str = translation_prompt):
        self._agent = TranslationAgent()

    def translate(self, text: str) -> str:
        return self._agent.translate(text)

class IdeasAgent:
    def __init__(self, sys_prompt: str = idea_prompt_openai):
        self._agent = _IdeaAgent()
        self.sys_prompt = sys_prompt

    def generate(self, topic: str, content_type: str, num_ideas: int = 10) -> str:
        # Use OpenAI path by default; other fields left empty
        return self._agent.generate_ideas_openai(
            num_ideas=num_ideas,
            sys_prompt_oa=self.sys_prompt,
            broad_topic=topic,
            content_type=content_type,
            brand_guidelines="",
            content_pillars="",
            example_ideas="",
            audience_comments="",
            enable_web_search=False,
            output_language="EN"
        )

class ContentAgent:
    def __init__(self, unified_prompt: str = content_prompt):
        self._agent = _UnifiedGenAgent(unified_prompt)

    def linkup_mode(self, mode: str):
        self._agent.linkup_output_type = mode

    def linkup_search(self, query: str) -> str:
        resp = self._agent.perform_linkup_search(query)
        return self._agent.format_linkup_response(resp)

    def generate(self, title: str, broad_topic: str, text_or_video: str, language: str,
                 brand_guidelines: str, structure_guidelines: str, tov_guidelines: str, editorial_standards: str, 
                 examples: str, supp_info: str, freq_terms: dict, enable_web_search: bool) -> str:
        return self._agent.generate_content(title, broad_topic, text_or_video, language,
                 brand_guidelines, structure_guidelines, tov_guidelines, editorial_standards, 
                 examples, supp_info, freq_terms, enable_web_search)

class ReviseAgent:
    def __init__(self, system_prompt: str = "You are a helpful editor that improves clarity, tone, and adherence to instructions."):
        self._agent = RevisionAgent(system_prompt)

    def revise(self, draft: str, instructions: str) -> str:
        return self._agent.suggest_revisions(draft, instructions)

class ComplianceAgent:
    def __init__(self, system_prompt: str = "You are a careful QA and legal compliance reviewer for social content."):
        self._agent = QALegalComplianceAgent(system_prompt)

    def check(self, draft: str, rules: str) -> str:
        # Using same 'rules' for both qa_standards and legal_guidelines here
        return self._agent.suggest_revisions(draft, qa_standards=rules, legal_guidelines=rules)
