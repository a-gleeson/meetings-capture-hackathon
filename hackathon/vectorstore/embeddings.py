import json

from langchain.embeddings import SagemakerEndpointEmbeddings
from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler

from config.logging import setup_logging

get_logger = setup_logging()
logger = get_logger(__name__)


# class for serializing/deserializing requests/responses to/from the embeddings model
class ContentHandler(EmbeddingsContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs={}) -> bytes:
        # "text_inputs"
        input_str = json.dumps({"text_inputs": prompt, **model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> str:

        response_json = json.loads(output.read().decode("utf-8"))
        embeddings = response_json["embedding"]
        if len(embeddings) == 1:
            return [embeddings[0]]
        return embeddings


def create_sagemaker_embeddings_from_hosted_model(
    embeddings_model_endpoint_name: str, aws_region: str
):
    # all set to create the objects for the ContentHandler and
    # SagemakerEndpointEmbeddingsJumpStart classes
    content_handler = ContentHandler()

    # note the name of the LLM Sagemaker endpoint, this is the model that we would
    # be using for generating the embeddings
    embeddings = SagemakerEndpointEmbeddings(
        endpoint_name=embeddings_model_endpoint_name,
        region_name=aws_region,
        content_handler=content_handler,
        model_kwargs={
            # "top_k": 2,
            "mode": "embedding",
            # "queries": "",
        },
    )
    return embeddings
