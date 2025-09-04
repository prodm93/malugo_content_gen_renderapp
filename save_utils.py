import os
import re
import ast
import streamlit as st
from anthropic import Anthropic
from typing import List
from pydantic import BaseModel
from agents.prompts import *

class STPost:
    def __init__(self, topic=None, content_type=None, language=None, idea=None, 
                 content_with_caption=None):
        self.idea = idea
        self.language = language
        self.content_type = content_type
        self.content_with_caption = content_with_caption
        self.topic = topic

class SupabasePost(BaseModel):
    idea: str
    outline: str
    copy: str
    rewrite: str
    caption: str
    topic: str
    content_type: str

def reset():
    st.session_state.current_post = STPost()
    st.session_state.current_topic = st.session_state.topic_choices[0]
    st.session_state.current_content_type = st.session_state.content_choices[0]
    st.session_state['idea_prompt_openai'] = idea_prompt_openai
    st.session_state['idea_prompt_claude'] = idea_prompt_claude
    st.session_state.content_prompt = content_prompt
    st.session_state['qa_legal_prompt'] = qa_legal_prompt
    
    if 'supp_info' in st.session_state.keys():
        del st.session_state['supp_info']

def extract_caption(full_output: str) -> List[str]:
        client = Anthropic(api_key = os.environ["anthropic_api_key"])
    
        system = f"""
            You are an expert copy editor and processor. Your task is to separate the post/script content and its accompanying caption, 
            and return them as two separate items in a Pythonic list without altering any of the text. Only return the list and nothing else."""
    
        Prompt = f"""
                Please extract the content and its caption:
                Full content output: --{full_output}--
            """
    
        message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4096,
                    system=system,
                    temperature=0,
                    messages=[
                        {"role": "user", "content": Prompt}
                ])
        try:
            result = ast.literal_eval(message.content[0].text)
        except SyntaxError:
            try:
                model_output = message.content[0].text.replace('"', "'")
                result = ast.literal_eval(model_output)
            except SyntaxError:
                try:
                    model_output = message.content[0].text.replace('"', '\"')
                    result = ast.literal_eval(model_output)
                except:
                    result = full_output.split('Caption:')
        return result
