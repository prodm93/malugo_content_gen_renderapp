import os
from agents.prompts import idea_prompt_openai, idea_prompt_claude
from openai import OpenAI
from anthropic import Anthropic

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

class IdeaAgent:
    def __init__(self):
        pass

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def generate_ideas_openai(self, num_ideas, sys_prompt_oa: str, broad_topic: str, content_type: str, 
                              brand_guidelines: str, content_pillars: str, example_ideas: str, 
                              audience_comments: str = "", enable_web_search: bool = False, output_language: str = 'EN'):
        """Generate social media content ideas using OpenAI with optional web search"""
        
        client = OpenAI()

        # Convert potential None values and pandas NaN to empty strings
        import pandas as pd
        
        def clean_value(val):
            if val is None or pd.isna(val) or str(val).lower() == 'nan':
                return ""
            return str(val)
        
        brand_guidelines = clean_value(brand_guidelines)
        content_pillars = clean_value(content_pillars)
        example_ideas = clean_value(example_ideas)
        audience_comments = clean_value(audience_comments)
        broad_topic = clean_value(broad_topic)
        content_type = clean_value(content_type)
        output_language = clean_value(output_language) if output_language else "EN"

        # Build the input prompt
        input_prompt = f"""
        System: {sys_prompt_oa.format(broad_topic=broad_topic)}
        
        Please generate {str(num_ideas)} social media content ideas for the specific topic. Answer with the ideas and nothing else:
        Output language: --{output_language}--
        Topic: --{broad_topic}--
        Content type: --{content_type}--
        Brand guidelines: ---{brand_guidelines}---
        Content pillars: ---{content_pillars}---
        Example ideas: --{example_ideas}--
        Audience comments (if any): --{audience_comments}--
        
        FINAL INSTRUCTION: Your response must start immediately with "1." followed by the first idea. Do not write any introductory text, research summaries, analysis, or commentary. Only provide the numbered list of content ideas.
        """

        if enable_web_search:
            # Configure tools for web search
            tools = []
            
            # Configure location based on output language
            user_location = None
            if output_language == "PT-BR":
                user_location = {
                    "type": "approximate",
                    "country": "BR",
                    "city": "São Paulo",
                    "region": "São Paulo"
                }
            
            # Build web_search tool
            web_search_tool = {
                "type": "web_search"
            }
            
            # Add user_location if specified
            if user_location:
                web_search_tool["user_location"] = user_location
            
            tools = [web_search_tool]
            
            # Add search strategy instruction
            search_instruction = f"""
            
            SEARCH STRATEGY REQUIREMENT: When conducting web searches, you MUST incorporate specific keywords from these content pillars: {content_pillars}. 
            Extract key concepts from these pillars and use them as search terms. For example, if pillars mention "attachment theory," search for "attachment theory dating trends 2025". If they mention "conscious relationships," search for "conscious dating social media 2025". 
            Conduct at least 3-4 searches using different pillar-specific keywords to ensure diverse coverage.
            """
            input_prompt += search_instruction

            # Use Responses API for web search
            response = client.responses.create(
                model="o4-mini",
                tools=tools,
                input=input_prompt
            )
            
            return response.output_text
        else:
            # Use Chat Completions API for non-web search requests
            messages = [
                {"role": "system", "content": sys_prompt_oa.format(broad_topic=broad_topic)},
                {"role": "user", "content": input_prompt}
            ]

            response = client.chat.completions.create(
                model="o4-mini",
                reasoning_effort="medium",
                messages=messages,
            )
            
            return response.choices[0].message.content

    def generate_ideas_claude(self, num_ideas, sys_prompt_claude: str, broad_topic: str, content_type: str, 
                              brand_guidelines: str, content_pillars: str, example_ideas: str, 
                              audience_comments: str = "", enable_web_search: bool = False, output_language: str = 'EN'):
        """insert function description here"""
        
        client = Anthropic(api_key = os.environ["anthropic_api_key"])

        system = sys_prompt_claude.format(broad_topic=broad_topic)

        # Convert potential None values and pandas NaN to empty strings
        import pandas as pd
        
        def clean_value(val):
            if val is None or pd.isna(val) or str(val).lower() == 'nan':
                return ""
            return str(val)
        
        brand_guidelines = clean_value(brand_guidelines)
        content_pillars = clean_value(content_pillars)
        example_ideas = clean_value(example_ideas)
        audience_comments = clean_value(audience_comments)
        broad_topic = clean_value(broad_topic)
        content_type = clean_value(content_type)
        output_language = clean_value(output_language) if output_language else "EN"

        Prompt = f"""
        Please generate {str(num_ideas)} social media content ideas for the specific topic. Answer with the ideas and nothing else:
        Output language: --{output_language}--
        Topic: --{broad_topic}--
        Content type: --{content_type}--
        Brand guidelines: ---{brand_guidelines}---
        Content pillars: ---{content_pillars}---
        Example ideas: --{example_ideas}--
        Audience comments (if any): --{audience_comments}--
        
        FINAL INSTRUCTION: Your response must start immediately with "1." followed by the first idea. Do not write any introductory text, research summaries, analysis, or commentary. Only provide the numbered list of content ideas.
        """

        # Define tools if web search is enabled
        tools = []
        if enable_web_search:
            # Configure location based on output language
            user_location = None
            if output_language == "PT-BR":
                user_location = {
                    "type": "approximate",
                    "city": "São Paulo",
                    "region": "São Paulo",
                    "country": "BR",
                    "timezone": "America/Sao_Paulo"
                }
            
            # Build web_search tool schema
            web_search_tool = {
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 5,
                "blocked_domains": ["reddit.com"]
            }
            
            # Add user_location if specified
            if user_location:
                web_search_tool["user_location"] = user_location
            
            tools = [web_search_tool]
        
        # Create message with or without tools
        message_params = {
            "model": 'claude-sonnet-4-20250514',
            "max_tokens": 4096,
            "thinking": {
                "type": "enabled",
                "budget_tokens": 3072
            },
            "system": system,
            "messages": [
                {"role": "user", "content": Prompt}
            ]
        }
        
        # Add tools if web search is enabled
        if enable_web_search:
            message_params["tools"] = tools
            
            # If PT-BR, also add instruction to search in Portuguese/for Brazilian content
            if output_language == "PT-BR":
                localised_instruction = """
                
                NOTE: Since the output language is Portuguese (Brazil), prioritize searching for Brazilian trends, Portuguese-language content, and topics relevant to the Brazilian market when conducting web searches.
                """
                message_params["messages"][0]["content"] += localised_instruction
            
            # Add strong instruction to skip commentary and use specific pillar keywords
            skip_commentary_instruction = f"""
            
            CRITICAL OUTPUT FORMAT: After completing your research, you must respond with ONLY the numbered list of ideas. Do not include:
            - Research summaries
            - Trend analysis 
            - Commentary about findings
            - Explanations of your process
            - Any text before the numbered list
            Start your response directly with "1." and continue with just the ideas.
            
            SEARCH STRATEGY REQUIREMENT: When conducting web searches, you MUST incorporate specific keywords from these content pillars: {content_pillars}. 
            Extract key concepts from these pillars and use them as search terms. For example, if pillars mention "attachment theory," search for "attachment theory dating trends 2025". If they mention "conscious relationships," search for "conscious dating TikTok 2025". 
            Conduct at least 3-4 searches using different pillar-specific keywords to ensure diverse coverage.
            """
            message_params["messages"][0]["content"] += skip_commentary_instruction
        
        message = client.messages.create(**message_params)
        
        text_content = ""
        
        # ========== DEBUG CODE START - REMOVE LATER ==========
        import streamlit as st
        st.write(f"Total content blocks: {len(message.content)}")
        for i, content_block in enumerate(message.content):
            st.write(f"Block {i}: Type = {getattr(content_block, 'type', 'no type')}")
            if hasattr(content_block, 'type'):
                if content_block.type == 'tool_use':
                    st.write(f"  Tool name: {getattr(content_block, 'name', 'no name')}")
                    st.write(f"  Tool input: {getattr(content_block, 'input', 'no input')}")
                    if hasattr(content_block, 'input') and 'query' in content_block.input:
                        st.write(f"  Search query used: {content_block.input['query']}")
                elif content_block.type == 'server_tool_use':
                    st.write(f"  Server tool name: {getattr(content_block, 'name', 'no name')}")
                    st.write(f"  Server tool input: {getattr(content_block, 'input', 'no input')}")
                    if hasattr(content_block, 'input') and 'query' in content_block.input:
                        st.write(f"  Search query used: {content_block.input['query']}")
                elif content_block.type == 'web_search_tool_result':
                    st.write(f"  Tool use ID: {getattr(content_block, 'tool_use_id', 'no id')}")
                    if hasattr(content_block, 'content'):
                        search_results = content_block.content
                        if isinstance(search_results, list):
                            st.write(f"  Search results ({len(search_results)} results):")
                            for j, result in enumerate(search_results[:5]):  # Show first 5
                                st.write(f"    Result {j+1}:")
                                # Try to access as dictionary first, then as object
                                if isinstance(result, dict):
                                    st.write(f"      URL: {result.get('url', 'no url')}")
                                    st.write(f"      Title: {result.get('title', 'no title')}")
                                    st.write(f"      Page age: {result.get('page_age', 'no age')}")
                                    st.write(f"      Type: {result.get('type', 'no type')}")
                                else:
                                    # Try object attributes
                                    st.write(f"      URL: {getattr(result, 'url', 'no url')}")
                                    st.write(f"      Title: {getattr(result, 'title', 'no title')}")
                                    st.write(f"      Page age: {getattr(result, 'page_age', 'no age')}")
                                    st.write(f"      Type: {getattr(result, 'type', 'no type')}")
                        else:
                            st.write(f"  Content type: {type(search_results)}")
                            st.write(f"  Content: {search_results}")
        # ========== DEBUG CODE END - REMOVE LATER ==========
        
        for content_block in message.content:
            # Check if the content block is a text block and has text attribute
            if hasattr(content_block, 'type') and content_block.type == 'text':
                if hasattr(content_block, 'text') and content_block.text is not None:
                    text_content += str(content_block.text)
            elif hasattr(content_block, 'text') and content_block.text is not None:
                text_content += str(content_block.text)
        
        return text_content if text_content else "No text content found in response"
