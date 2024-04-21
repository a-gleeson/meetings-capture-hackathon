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
    OpensearchClientStore,
    OpenSearchStore,
)
from hackathon.vectorstore.vestorstore_loader import VectorstoreLoader

# from botocore.exceptions import ClientErrors


get_logger = setup_logging()
logger = get_logger(__name__)
cwd = os.getcwd()

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
