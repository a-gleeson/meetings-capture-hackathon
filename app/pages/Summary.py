import base64
import datetime as dt
import io
import os

import streamlit as st
from PIL import Image
from streamlit_gov_uk_components import gov_uk_checkbox

from config.logging import setup_logging
from config.settings import ENV
from hackathon.streamlit.utils import check_password
from hackathon.transcripts.transcript_handling import Transcript

get_logger = setup_logging()
logger = get_logger(__name__)

st.set_page_config(page_title="", page_icon="🎯", layout="wide")

# Password protection of pages
if ENV.upper() == "PROD" and not check_password():
    st.stop()  # Do not continue if check_password is not True.


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


cwd = os.getcwd()
image_path = os.path.join(cwd, "static", "images", "gov_uk.png")
image = Image.open(image_path)

header_css = """
    <style>
        .header {
            color: white;
            background-color: black;
            padding: 0px;
            display: flex;
            align-items: center;
            height: 60px; /* Fixed height for the header */
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
            <img src="data:image/png;base64,{image_to_base64(image)}" width="200">  <!-- Adjust width as needed -->
            <p>Civil Service Jobs</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

# Blue underline section
st.markdown('<div class="blue-underline"></div>', unsafe_allow_html=True)

# CSS for the alpha box
alpha_css = """
    <style>
        .alpha-box {
            display: flex;
            align-items: center;
            font-family: Arial, Helvetica, sans-serif;
            margin-top: -15px; /* Add space above the alpha box */
            margin-left: 75px; /* Adjustable left margin */
        }
        .alpha {
            background-color: #1d70b8; /* Blue color */
            color: white;
            padding: 3px 6px;
            font-size: 14px;
            font-weight: bold; /* Make ALPHA text bold */
            border-radius: 0px;
            margin-right: 10px; /* Space between ALPHA box and text */
        }
    </style>
"""

# Add the CSS to the page
st.markdown(alpha_css, unsafe_allow_html=True)

# Create the alpha box section
st.markdown(
    """
    <div class="alpha-box">
        <span class="alpha">DISCOVERY</span>
        <span>Your feedback will help us to improve.</span>
    </div>
""",
    unsafe_allow_html=True,
)

# Apply custom styles to the sidebar using st.markdown
sidebar_css = """
    <style>
        .sidebar {
            background-color: black;
            color: white;
        }
    </style>
"""

st.markdown(sidebar_css, unsafe_allow_html=True)
st.sidebar.success("Select a page above")

# * [Initialise the data](/initialise_the_data) will load in the previous vacancies from s3.


def llm_summarise() -> str:
    return "This is a summary"


def query_llm(prompt: str) -> str:

    return f'Hello! I am *not* an LLM! James created me as an "artificial artificial intelligence" - this is the only thing I can say. ({dt.datetime.now()})'


with st.container():
    data_path = st.file_uploader(label="Upload transcript:")
    if data_path is not None:
        transcript = Transcript(data_path)
        data = str(transcript)
        st_summarise_button = st.button("Summarise")
        if st_summarise_button or st.session_state.summary_generated:
            st.session_state.summary_generated = True
            st.markdown(llm_summarise())
            prompt = st.text_input(label="Enter query here:")
            st_query_button = st.button("Query LLM")
            if st_query_button and prompt != "":
                st.session_state.chat_history += f"User: {prompt}\n\n"
                st.session_state.chat_history += f"Claude: {query_llm(prompt)}\n\n"
                st.markdown(st.session_state.chat_history)
