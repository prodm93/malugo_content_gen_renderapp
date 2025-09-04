import os
from typing import List, Dict, Literal
from linkup import LinkupClient
from anthropic import Anthropic
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

class UnifiedGenAgent: 
    def __init__(self, unified_prompt):
        self.model = 'claude-sonnet-4-20250514'
        self.unified_prompt = unified_prompt
        self.linkup_output_type: Literal["searchResults", "sourcedAnswer"] = "searchResults"
    
    def linkup_web_search(self, query: str) -> str:
        client = LinkupClient(api_key=os.environ['LINKUP_API_KEY'])
      
        response = client.search(
            query=query,
            depth="standard",
            output_type=self.linkup_output_type
        )
        return response
    
    def format_linkup_response(self, response, output_type: Literal["searchResults", "sourcedAnswer"] = None) -> str:
        if output_type is None:
            output_type = self.linkup_output_type
            
        if output_type == "sourcedAnswer":
            return response.answer
        elif output_type == "searchResults":
            results = getattr(response, "results", [{"content": "No answer provided."}])
            answer = "\n".join([f"{i}. {doc.content}" for i, doc in enumerate(results, start=1)])
            return f'Search Results:\n{answer}'
    
    def perform_web_search(self, title: str) -> str:
        """Perform web search based on the content title and return formatted results."""
        try:
            # Search for recent information about the topic
            search_response = self.linkup_web_search(title)
            formatted_results = self.format_linkup_response(search_response)         
            return "\n\n".join([formatted_results])
            
        except Exception as e:
            print(f"Web search failed: {e}")
            return "Web search was not successful. Proceeding without additional research context."
          
    #@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def generate_content(self, title: str, broad_topic: str, text_or_video: str, language: str,
                         brand_guidelines: str, structure_guidelines: str, tov_guidelines: str, editorial_standards: str, 
                         examples: str, supp_info: str, freq_terms: dict, enable_web_search: bool):
        client = Anthropic(api_key=os.environ["anthropic_api_key"])
        
        base_prompt = f"""
        Please generate content based on the following information:
        Title of the content: --{title}--
        Broad topic: --{broad_topic}--
        Type of content: --{text_or_video}--
        Output language: --{language}--
        Brand guidelines: --{brand_guidelines}--
        Content structure guidelines: --{structure_guidelines}--
        Tone-of-voice guidelines: --{tov_guidelines}--
        Editorial and quality assurance standards: --{editorial_standards}--
        Example posts: <examples>--{examples}--</examples>
        Supplemental information: --{supp_info}--
        Dictionary of frequent words and phrases from previous posts: --{freq_terms}--
        """
        
        # Add web search results if enabled
        if enable_web_search:
            #print(f"Performing web search for: {title}")
            web_search_results = self.perform_web_search(title)
            enhanced_prompt = f"""
            {base_prompt}
            
            Recent web search results for additional context:
            <web_search_results>
            {web_search_results}
            </web_search_results>
            
            Please incorporate relevant insights from the web search results into your content generation process, ensuring all information is credible and adds value to the content.
            """
        else:
            enhanced_prompt = base_prompt
        
        message = client.messages.create(
            model=self.model,
            max_tokens=20000,
            thinking={
                "type": "enabled",
                "budget_tokens": 16000
            },
            system=self.unified_prompt,
            messages=[
                {"role": "user", "content": enhanced_prompt}
            ]
        )
        return message.content[-1].text
