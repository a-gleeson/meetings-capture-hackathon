import base64
import io
import os

import streamlit as st
from PIL import Image

from config.logging import setup_logging

get_logger = setup_logging()
logger = get_logger(__name__)

st.set_page_config(page_title="QuickQuill", page_icon="memo", layout="wide")

# Image loading
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


cwd = os.getcwd()
logo_path = os.path.join(cwd, "static", "images", "logo.png")
logo = Image.open(logo_path)

header_css = """
    <style>
        .header {
            color: white;
            background-color: black;
            padding: 0px;
            display: flex;
            align-items: center;
            height: 160px; /* Fixed height for the header */
            text-align: center;
        }
        .header img {
            margin-left: 10px;
            margin-right: 100px;  /* Adjust spacing between image and text */
        }
        .header p {
            margin: 0;
            font-size: 80px; /* Adjust font size as needed */
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
            <img src="data:image/png;base64,{image_to_base64(logo)}" width="140">
            <p>QuickQuill</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
            <h2 style="font-family: Arial, Helvetica, sans-serif; color: black;">Create faster, easier, better meeting records.</h2>
            """,
    unsafe_allow_html=True,
)

st.markdown("##")

col1, col2 = st.columns([1, 1])
with col1:
    st.image(os.path.join("static", "images", "cabinet-meeting.png"))
with col2:
    st.markdown(
        "<p text-align: justify; text-justify: inter-word;>"
        "This is a tool to take in meeting recordings and generate transcripts, leveraging the power of AI. "
        "Once a transcript is generated, the app can be used to make edits to timestamps, speakers, and items.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p text-align: justify; text-justify: inter-word;>"
        "The app further utilises LLMs to generate iterative summaries of topics discussed during meetings, "
        "and identifies key facts and statistics raised during the meeting that need to be scrutinised further."
        "</p>",
        unsafe_allow_html=True,
    )
