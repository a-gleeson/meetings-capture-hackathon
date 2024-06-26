import base64
import datetime as dt
import io
import os
import time

import streamlit as st
from PIL import Image

from config.logging import setup_logging
from config.settings import ENV
from hackathon.llm.llm_api import conversation_api, fact_check_api, glossery_api, summary_api
from hackathon.transcripts.transcript_handling import Transcript

get_logger = setup_logging()
logger = get_logger(__name__)

st.set_page_config(page_title="QuickQuill", page_icon="memo", layout="wide")

# Image loading
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


if "chat_history" not in st.session_state:
    st.session_state.chat_history = ""
if "summary_generated" not in st.session_state:
    st.session_state.summary_generated = False
if "transcript_uploaded" not in st.session_state:
    st.session_state.transcript_uploaded = False
if "transcript_uploaded" not in st.session_state:
    st.session_state.transcript_uploaded = False


cwd = os.getcwd()
logo_path = os.path.join(cwd, "static", "images", "logo.png")
image = Image.open(logo_path)
logo_path = os.path.join(cwd, "static", "images", "logo.png")
image = Image.open(logo_path)

header_css = """
    <style>
        .header {
            color: white;
            background-color: black;
            padding: 0px;
            display: flex;
            align-items: center;
            height: 60px; /* Fixed height for the header */
            text-align: center;
        }
        .header img {
            margin-right: 120px;  /* Adjust spacing between image and text */
        }
        .header p {
            margin: 0;
            font-size: 25px; /* Adjust font size as needed */
            line-height: 1.0; /* Adjust line height to match image height */
            font-weight: bold; /* Make text bold */
            font-family: Arial, Helvetica, sans-serif; /* Set font family */
            text-align: center;
            padding: 20px;
        }
        .blue-underline {
            background-color: #1d70b8; /* Blue color for the underline */
            height: 8px; /* Height of the underline */
            width: 85%; /* Set the width of the underline */
            margin: 0 auto; /* Center the underline horizontally */
        }
        .normal-line {
            background-color: #dddddd; /* Neutral color for the line */
            height: 2px; /* Thin line */
            width: 85%; /* Set the width of the line */
            margin: 10px auto 0; /* Add top margin to push the line down */
        }
    </style>
"""
st.markdown(header_css, unsafe_allow_html=True)

# Create a header section
header = st.container()
with header:
    # Using HTML to layout image and text
    st.markdown(
        f"""
        <div class="header">
            <p>QuickQuill</p>
        </div>
    """,
        unsafe_allow_html=True,
    )
st.markdown(
    """
            <h2 style="font-family: Arial, Helvetica, sans-serif; color: black;">Create meeting summary</h2>
            """,
    unsafe_allow_html=True,
)


def llm_summarise(transcript: str) -> str:
    post_response = summary_api.invoke_post(transcript)
    fact_check_response = fact_check_api.invoke_post(transcript)
    conversation_response = conversation_api.invoke_post(transcript)
    time.sleep(20)

    get_summary_response = summary_api.invoke_get(post_response["conversationId"])
    get_fact_response = fact_check_api.invoke_get(fact_check_response["conversationId"])

    post_glossary = glossery_api.invoke_post(get_summary_response)
    time.sleep(25)
    time.sleep(25)
    get_glossary = glossery_api.invoke_get(post_glossary["conversationId"])
    conversation_api.invoke_get(conversation_response["conversationId"])
    conversation_api.invoke_get(conversation_response["conversationId"])
    return {
        "summary": get_summary_response,
        "facts": get_fact_response,
        "glossary": get_glossary,
        "conversationConversationId": conversation_response["conversationId"],
        "conversationConversationId": conversation_response["conversationId"],
    }
        "summary": get_summary_response,
        "facts": get_fact_response,
        "glossary": get_glossary,
        "conversationConversationId": conversation_response["conversationId"],
    }



def query_llm(prompt: str, transcript: str, conversationId) -> str:
    query = f"With knowledge of this transcript:\n{transcript}\n\nAnswer this query: {prompt}"
    print(query)
    query_response = conversation_api.invoke_post(query, conversationId)
    time.sleep(15)
    chat_response = conversation_api.invoke_get(query_response["conversationId"])
    return chat_response

data= ""
with st.expander("#### Upload transcript", expanded=True):
    data_path = st.file_uploader(label="Upload transcript:")
    if data_path is not None:
        transcript = Transcript(data_path)
        data = str(transcript)
        st.session_state.transcript_uploaded = True

returned_data = {}
with st.expander("#### Generate summary", expanded=True):
    if not st.session_state.transcript_uploaded:
        st.error("Upload meeting transcript", icon="⚠️")
    else:
        st_summarise_button = st.button("Generate meeting summary")
        if st_summarise_button or st.session_state.summary_generated:
            if not st.session_state.summary_generated:
                returned_data = llm_summarise(transcript=data)
                st.session_state.returned_data = returned_data
            returned_data = st.session_state.returned_data
            if not st.session_state.summary_generated:
                returned_data = llm_summarise(transcript=data)
                st.session_state.returned_data = returned_data
            returned_data = st.session_state.returned_data
            st.session_state.summary_generated = True
            st.markdown(returned_data["summary"])
            prompt = st.text_input(label="Enter query here:", placeholder="How ")
            st_query_button = st.button("Query LLM")
            if st_query_button and prompt != "":
                st.session_state.chat_history += f"User: {prompt}\n\n"
                st.session_state.chat_history += f"Claude: {query_llm(prompt, data, conversationId=returned_data['conversationConversationId'])}\n\n"
                st.session_state.chat_history += f"Claude: {query_llm(prompt, data, conversationId=returned_data['conversationConversationId'])}\n\n"
                st.markdown(st.session_state.chat_history)
            # TODO: Add button to download summary as txt file

with st.expander("#### Identify facts", expanded=False):
    if returned_data.get("facts") and st.session_state.summary_generated:
        returned_data = st.session_state.returned_data
        st.write(returned_data["facts"])

with st.expander("#### Generate glossary", expanded=False):
    if returned_data.get("glossary") and st.session_state.summary_generated:
        returned_data = st.session_state.returned_data
        st.write(returned_data["glossary"])
