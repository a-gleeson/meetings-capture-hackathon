import streamlit as st

from config.logging import setup_logging
from config.settings import ENV
from hackathon.streamlit.utils import check_password

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
            <h2 style="font-family: Arial, Helvetica, sans-serif; color: black;">Welcome!</h2>
            """,
    unsafe_allow_html=True,
)
st.write("Select a page to the left to get started.")
