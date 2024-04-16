from dataclasses import dataclass
from operator import itemgetter
from typing import Dict, List

from langchain.schema.output_parser import StrOutputParser
from langchain_core.output_parsers.transform import BaseTransformOutputParser

from hackathon.llm.prompts.core import (
    PromptTemplate,
)


@dataclass
class ChainType:
    """
    A Chain type that a ChainConfig can be set to, this will determine which LLM Chain this config is set up with.
    """

    identifier: str
    description: str


SINGLE_CHAIN = ChainType(
    identifier="SINGLE_CHAIN",
    description="A simple chain which takes var_input for the prompt, a prompt, llm and an output parser",
)


@dataclass
class ChainConfig:
    """
    Configuration for an LLM chain.
    The class uses a custome initilisation method to set up various cnfiguration parameters.

    Attributes:
        name (str): The name of the LLM chain.
        prompt (PromptTemplate): prompt template for the chain to use
        input_values (List[str]): input values the prompt takes
        input_format (str) = format of the input for the input values defaults to 'Dict' (Currently not functional)
        out_parser (BaseTransformOutputParser) = output parser for the LLM Chain to use.
    """

    name: str
    prompt: PromptTemplate
    input_values: List[str]
    input_format: str = "Dict"
    # context:Optional[str]  = None
    out_parser: BaseTransformOutputParser = StrOutputParser
    chain_type: ChainType = SINGLE_CHAIN

    def __init__(
        self,
        name: str,
        prompt: PromptTemplate,
        chain_type: ChainType = SINGLE_CHAIN,
        input_values: List[str] = ["input"],
        input_format: str = "Dict",
        # context: Optional[str] = None,
        out_parser=StrOutputParser,
    ):
        self.name = name
        self.prompt = prompt
        self.input_format = input_format
        self.var_input = {key: itemgetter(key) for key in input_values}
        self.out_parser = out_parser
        self.chain_type = chain_type


# ADVICE_CHAIN = ChainConfig(
#     name="advice",
#     prompt=ADVICE_PROMPT,
#     input_values=["job_description", "advice", "context"],
# )
