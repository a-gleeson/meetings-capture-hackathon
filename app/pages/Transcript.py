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

st.set_page_config(page_title="Meeting Record Creator", page_icon="🎯", layout="wide")

# Password protection of pages
if ENV.upper() == "PROD" and not check_password():
    st.stop()  # Do not continue if check_password is not True.


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


st.header("Edit Meeting Transcript")


data_path = st.file_uploader(label="#### Transcript `.csv`")
if data_path is not None:
    transcript = Transcript(data_path)
    data = transcript.data

    with st.expander("Edit meeting attendees", expanded=False):
        speaker_list = data["Speaker"].unique()
        edited_speaker_list = st.data_editor(speaker_list, num_rows="dynamic")

    with st.expander("Edit meeting transcript", expanded=False):
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
        if st.button("Approve transcript"):
            transcript.update_data(st_transcript_table)
            st.success("Transcription approved")
            st.download_button(
                "Download transcript as .txt file",
                data=str(transcript),
                file_name="transcript_download.txt",
            )
