from abc import ABC
from typing import Dict

from langchain_core.runnables import RunnableSequence

from config.logging import setup_logging
from hackathon.llm.chain_config import SINGLE_CHAIN, ChainConfig
from hackathon.llm.llm import LLM

get_logger = setup_logging()
logger = get_logger(__name__)


class TokenLimitExceeded(Exception):
    """Exception for if the token limit is exceeded."""

    pass


class LLMChain(ABC):
    """Class for a simple LLMChain, can be inherited for more complex implementations."""

    def __init__(self, config: ChainConfig, llm: LLM):
        """
        Attributes:
            config (ChainConfig): configuration for the llm chain being initialised.
            llm (LLM): to attach to the LLMChain
        """
        self.chain: RunnableSequence = (
            config.var_input
            | config.prompt
            | llm.get_llm()
            | config.out_parser()
        )

    def invoke_query(self, query: Dict):
        """
        Invokes query against chain.

        Args:
            query (Dict): dictionary object for the input variables for the llm chain.
        Raises:
            TokenLimitExceeded: If LLM token limit has been exceeded.
        """
        try:
            response = self.chain.invoke(query)
            logger.debug("query result %s", response)
        except Exception as e:
            logger.error(e)
            raise TokenLimitExceeded(e)
            # message = json.loads(e.message)
            # if message.error_type == "validation" and "tokens" in message.error:
            #     raise TokenLimitExceeded(e)
        return response


class LLMChainFactory:
    """
    A static class which will create a specific LLM chain with a config,
    depending on the chain_type set in the config. With a given llm.
    """

    @staticmethod
    def create_chain(config: ChainConfig, llm: LLM) -> LLMChain:
        """
        Args:
            config (ChainConfig): config for the LLM Chain
            llm (LLM): llm to attach to the LLM Chain
        Raises:
            ValueError: if `chain_type` is invalid.
        """
        chain = ""
        if config.chain_type == SINGLE_CHAIN:
            chain = LLMChain(config, llm)
        else:
            raise ValueError("Invalid Chain type set on the ChainConfig")
        return chain
