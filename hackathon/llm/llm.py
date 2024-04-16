import json
from abc import ABC, abstractmethod, abstractproperty
from typing import List

import boto3
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import LlamaCpp, SagemakerEndpoint
from langchain.llms.sagemaker_endpoint import LLMContentHandler

from config.logging import setup_logging
from config.settings import AWS_REGION, AWS_SAGEMAKER_ENDPOINT

get_logger = setup_logging()
logger = get_logger(__name__)


class LLM(ABC):

    @abstractmethod
    def get_llm(self):
        raise NotImplementedError()

    @abstractmethod
    def initialise_llm(self):
        raise NotImplementedError()


class LLama2(LLM):
    """
    https://python.langchain.com/docs/integrations/llms/llamacpp
    improve performance https://python.langchain.com/docs/integrations/llms/llm_caching
    """

    def __init__(
        self, llm_model_path: str, stop_sequences: List[str] = ["ANSWER:"]
    ) -> None:
        self.llm_model_path = llm_model_path
        self.callback_manager = CallbackManager(
            [StreamingStdOutCallbackHandler()]
        )
        self.stop_sequences = stop_sequences
        self.initialise_llm()

    def initialise_llm(self):
        logger.debug("Initialising local LLama2 LLM.")
        self.llm = LlamaCpp(
            n_ctx=5120 * 2,
            model_path=self.llm_model_path,
            n_gpu_layers=40,  # Change this value based on your model and your GPU VRAM pool.
            n_batch=512,  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
            callback_manager=self.callback_manager,
            verbose=True,
            model_kwargs={"max_new_tokens": 64 * 4},
            stop=self.stop_sequences,
        )

    def get_llm(self) -> object:
        return self.llm


class ContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs) -> bytes:
        input_str = json.dumps({"inputs": prompt, "parameters": model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json[0]["generated_text"]


class SagemakerHostedLLM(LLM):
    def __init__(self, endpoint_name, region, stop_sequences=[]) -> None:
        self.endpoint_name = endpoint_name
        self.region = region
        self.content_handler = ContentHandler()
        self.llm = None
        self.stop_sequences = stop_sequences
        self.initialise_llm()

    def initialise_llm(self, **kwargs):
        self.llm = SagemakerEndpoint(
            endpoint_name=self.endpoint_name,
            region_name=self.region,
            model_kwargs={"max_new_tokens": 64 * 20, "temperature": 0.01},
            endpoint_kwargs={"CustomAttributes": "accept_eula=true"},
            content_handler=self.content_handler,
            **kwargs
        )

    def get_llm(self) -> object:
        return self.llm
