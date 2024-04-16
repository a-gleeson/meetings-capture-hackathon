import base64
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

st.set_page_config(page_title="Meeting Record Creator", page_icon="memo", layout="wide")

# Password protection of pages
if ENV.upper() == "PROD" and not check_password():
    st.stop()  # Do not continue if check_password is not True.

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
            <p>Meeting Record Creator</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
            <h2 style="font-family: Arial, Helvetica, sans-serif; color: black;">Edit Meeting Transcript</h2>
            """,
    unsafe_allow_html=True,
)

st.session_state["transcript_uploaded"] = False

with st.expander("#### Upload audio recording", expanded=False):
    audio_file = st.file_uploader(
        "Upload meeting recording audio file", type=[".mp3", ".wav", ".m4a"]
    )
    if audio_file is not None:
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/wav")

with st.expander("#### Upload transcript", expanded=False):
    data_path = st.file_uploader(label="Upload transcript")
    if data_path is not None:
        transcript = Transcript(data_path)
        data = transcript.data
        st.session_state["transcript_uploaded"] = True

with st.expander("#### Edit meeting attendees", expanded=False):
    if st.session_state.transcript_uploaded:
        speaker_list = data["Speaker"].unique()
        edited_speaker_list = st.data_editor(speaker_list, num_rows="dynamic")
    else:
        st.error("Upload meeting transcript", icon="⚠️")

with st.expander("#### Edit meeting transcript", expanded=False):
    if st.session_state.transcript_uploaded:
        st_transcript_table = st.data_editor(
            data,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Speaker": st.column_config.SelectboxColumn(
                    "Speaker",
                    help="Select Speaker",
                    options=list(edited_speaker_list),
                    required=True,
                )
            },
        )
        if st.button("Approve transcript", type="primary"):
            transcript.update_data(st_transcript_table)
            st.success("Transcription approved")
            st.download_button(
                "Download transcript as .txt file",
                data=str(transcript),
                file_name="transcript_download.txt",
            )
    else:
        st.error("Upload meeting transcript", icon="⚠️")
