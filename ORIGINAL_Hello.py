import streamlit as st
import pandas as pd
from save_utils import *
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader

with open('./credentials.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 850px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)

authenticator.login()

if st.session_state["authentication_status"]:
    authenticator.logout()
    
    st.title("Agent-Based Content Generation System")

    st.subheader(f'Welcome, *{st.session_state["name"].split()[0]}*')

    st.divider()

    # Change this later--otherwise posts with some attributes missing (e.g. only outline or caption generated) will get handled the 
    # same way as a fully done post:
    st.session_state.current_post = STPost()
    
    with open('./default_guidelines/brand_guidelines.txt', 'r') as f:
        default_bg = f.read()
    with open('./default_guidelines/editorial_standards.txt', 'r') as f:
        default_es = f.read()
    with open('./default_guidelines/hashtag_guidelines.txt', 'r') as f:
        default_eg = f.read()
    with open('./default_guidelines/caption_examples.txt', 'r') as f:
        default_ce = f.read()
    with open('./default_guidelines/qa_guidelines.txt', 'r') as f:
        default_qa = f.read()
    with open('./default_guidelines/legal_compliance_guidelines.txt', 'r') as f:
        default_lcg = f.read()

    default_values = [default_bg, default_es, default_eg, default_ce, default_qa, default_lcg]
    
    with st.expander('Langauge & Guideline Inputs'):
        with st.sidebar.form(key='guidelines_form', clear_on_submit=False):
            output_language = st.radio('Language of Generated Content: ', ['EN', 'PT-BR'], index=0)
            labels = ['Brand Guidelines', 'Editorial Standards', 'Engagement Guidelines', 'Caption Examples', 'Quality Assurance Standards', 'Legal Compliance Guidelines']
            input_list = []
            for i, input_field in enumerate(labels):
                input_list.append(st.text_area(labels[i], value=default_values[i], height=200, key=i))

            submitted = st.form_submit_button(label="Submit", help=None, on_click=None, type="secondary", disabled=False)

            if submitted:
                st.session_state['output_language'] = output_language
                st.session_state['brand_guidelines'] = input_list[0] 
                st.session_state['editorial_standards'] = input_list[1]
                st.session_state['engagement_guidelines'] = input_list[2]
                st.session_state['caption_examples'] = input_list[3]
                st.session_state['qa_standards'] = input_list[4] 
                st.session_state['legal_guidelines'] = input_list[5]

    if 'topic_choices' not in st.session_state:
        st.session_state['topic_choices'] = ['Body and well-being', 'Personal and interpersonal development', 'Sex, love and relationships']
    if 'content_choices' not in st.session_state:
        st.session_state['content_choices'] = ['TikTok video', 'Instagram carousel', 'Instagram reel']

    uploaded_pillars = st.file_uploader('Content Pillars with Examples', type=None, accept_multiple_files=False, key='pillars', help=None, label_visibility="visible")
    if uploaded_pillars is not None:
        pillars_df = pd.read_excel(uploaded_pillars)
        st.session_state['pillars_df'] = pillars_df
    else:
        st.session_state['pillars_df'] = pd.read_excel('./default_guidelines/pillars_and_examples.xlsx')
        
    uploaded_structure_gd = st.file_uploader('Content Structure Guidelines', type=None, accept_multiple_files=False, key='structure', help=None, label_visibility="visible")
    if uploaded_structure_gd is not None:
        struct_df = pd.read_excel(uploaded_structure_gd)
        st.session_state['struct_df'] = struct_df
    else:
        st.session_state['struct_df'] = pd.read_excel('./default_guidelines/content_structure_guidelines.xlsx')

    uploaded_tov_gd = st.file_uploader('Tone-of-Voice Guidelines', type=None, accept_multiple_files=False, key='tov', help=None, label_visibility="visible")
    if uploaded_tov_gd is not None:
        tov_df = pd.read_excel(uploaded_tov_gd)
        st.session_state['tov_df'] = tov_df
    else:
        st.session_state['tov_df'] = pd.read_excel('./default_guidelines/tov_guidelines.xlsx')

    #st.write(st.session_state.brand_guidelines[:100])


elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')

