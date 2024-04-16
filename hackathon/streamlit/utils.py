import hmac
import json
import os
from ast import literal_eval
from io import BytesIO

import boto3
import folium
import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from folium.plugins import StripePattern
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from streamlit.runtime import get_instance
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit_folium import folium_static

from config.logging import setup_logging
from config.settings import (
    AWS_REGION,
    AWS_SAGEMAKER_ENDPOINT,
    EMBEDDING_ENDPOINT_NAME,
    LLM_MODEL,
    LOADER_CONFIG,
    OPENSEARCH_ENDPOINT_NAME,
    OPENSEARCH_INDEX_NAME,
    OPENSEARCH_SKILLS_INDEX_NAME,
    PROJECT_PATH,
    S3_LOADER_BUCKET,
    S3_LOADER_FILE_NAME,
    VECTOR_STORE_CONFIG,
)

# from hackathon.llm.chain_config import (
# # Empty for now
# )
from hackathon.llm.llm import LLama2, SagemakerHostedLLM
from hackathon.llm.llm_handler import LLMRunner
from hackathon.loader.chunker import TextChunker
from hackathon.loader.loader import FileLoader, S3Loader
from hackathon.vectorstore.embeddings import (
    create_sagemaker_embeddings_from_hosted_model,
)
from hackathon.vectorstore.opensearch import OpensearchClient
from hackathon.vectorstore.vectorstore import (
    ChromaClient,
    ChromaStore,
    OpensearchClientStore,
    OpenSearchStore,
)
from hackathon.vectorstore.vestorstore_loader import VectorstoreLoader

# from botocore.exceptions import ClientErrors


get_logger = setup_logging()
logger = get_logger(__name__)
cwd = os.getcwd()


def _get_session():
    runtime = get_instance()
    session_id = get_script_run_ctx().session_id
    session_info = runtime._session_mgr.get_session_info(session_id)
    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")
    return session_info.session


def get_password():
    secret_name = "streamlit-access-password"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=AWS_REGION)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = json.loads(get_secret_value_response["SecretString"])
    return secret["streamlit-access-password"]


def check_password():
    """Returns `True` if the user had the correct password."""
    logger.debug("Checking password ... ")

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], get_password()):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        logger.debug("password correct ...")
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        logger.debug("password incorrect ...")
        st.error("😕 Password incorrect")
    return False


def initialise_llm_runner():
    # Initialise the new embedder
    logger.info("Initialising LLM Runner...")
    if LLM_MODEL == "local_llm":
        st_embedder = SentenceTransformerEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    else:
        st_embedder = create_sagemaker_embeddings_from_hosted_model(
            EMBEDDING_ENDPOINT_NAME, AWS_REGION
        )

    if VECTOR_STORE_CONFIG == "chroma":
        vector_store = ChromaStore(
            embedding_function=st_embedder,
            collection_name=OPENSEARCH_INDEX_NAME,
        )
    else:
        if "skills_os_client" not in st.session_state:
            st.session_state["skills_os_client"] = OpensearchClient(
                OPENSEARCH_SKILLS_INDEX_NAME,
                OPENSEARCH_ENDPOINT_NAME,
                AWS_REGION,
            )
        if "vacancy_os_client" not in st.session_state:
            st.session_state["vacancy_os_client"] = OpensearchClient(
                OPENSEARCH_INDEX_NAME, OPENSEARCH_ENDPOINT_NAME, AWS_REGION
            )

        vector_store = OpenSearchStore(
            st_embedder,
            OPENSEARCH_INDEX_NAME,
            st.session_state["vacancy_os_client"],
        )

    if LLM_MODEL == "local_llm":
        llm_model_path = f"{PROJECT_PATH}/models/llama-2-7b-chat.Q4_K_M.gguf"
        llm = LLama2(
            llm_model_path=llm_model_path,
            stop_sequences=["ANSWER:", "\nHuman:", "\n```\n"],
        )
    else:
        llm = SagemakerHostedLLM(AWS_SAGEMAKER_ENDPOINT, AWS_REGION, ["==="])

    llm_runner = LLMRunner(
        llm=llm,
        vectorstore=vector_store,
        chain_configs=[],
    )
    st.session_state["runner"] = llm_runner


def initialise_vector_store_loader():
    if LLM_MODEL == "local_llm":
        st_embedder = SentenceTransformerEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    else:
        st_embedder = create_sagemaker_embeddings_from_hosted_model(
            EMBEDDING_ENDPOINT_NAME, AWS_REGION
        )

    if VECTOR_STORE_CONFIG == "chroma":
        vector_store = ChromaClient(st_embedder, OPENSEARCH_INDEX_NAME)
    else:
        if "vacancy_os_client" not in st.session_state:
            st.session_state["vacancy_os_client"] = OpensearchClient(
                OPENSEARCH_INDEX_NAME, OPENSEARCH_ENDPOINT_NAME, AWS_REGION
            )
        vector_store = OpensearchClientStore(
            st_embedder,
            OPENSEARCH_INDEX_NAME,
            st.session_state["vacancy_os_client"],
        )

    if LOADER_CONFIG == "file_loader":
        loader = FileLoader()
    elif LOADER_CONFIG == "s3_loader":
        loader = S3Loader(
            S3_LOADER_BUCKET,
        )
    else:
        raise ValueError("Invalid loader configured")

    st.session_state["vs_loader"] = VectorstoreLoader(
        vectorstore_client=vector_store,
        loader=loader,
        chunker=TextChunker(chunk_size=1000, overlap=10),
    )


def safe_literal_eval(x):
    try:
        return literal_eval(x)
    except (SyntaxError, ValueError):
        return None
