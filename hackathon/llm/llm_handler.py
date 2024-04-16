from typing import Dict, List

from config.logging import setup_logging
from hackathon.llm.chain_config import ChainConfig
from hackathon.llm.llm import LLM
from hackathon.llm.llm_chains import LLMChain, LLMChainFactory
from hackathon.vectorstore.vectorstore import VectorStore

get_logger = setup_logging()
logger = get_logger(__name__)


class LLMRunner:
    """
    A class for running a set of llm chains.
    """

    def __init__(
        self,
        llm: LLM,
        vectorstore: VectorStore,
        chain_configs: List[ChainConfig],
    ) -> None:
        """
        Sets up runner with required components of an llm, vectorstore and a list of llm chain configs.
        Attributes:
            llm (LLM): The llm the runner is using (Will be deprecated later for individual llms for chains).
            vectorstore (VectorStore): vectorstore that LLM chains can utilise if required.
            chain_configs (List[ChainConfig]) list of the llm chains that will be set up in runner.
        """
        self.llm = llm
        self.vectorstore = vectorstore
        self.chains = {
            config.name: LLMChainFactory.create_chain(config, self.llm)
            for config in chain_configs
        }

    def initialise_components(self):
        """
        Initialise the LLM, sometimes an llm needs set up before it can be used.
        """
        self.llm.initialise_llm()

    def query(self, query: Dict, chain: ChainConfig):
        """
        Execute a query on a given chain.

        Args:
            query (Dict): dictionary object for the input variables for the llm chain.
            chain (ChainConfig): chain config that the chain is stored under.
        Raises:
            ValueError: if `chain.name` is not found.
        """
        chain: LLMChain = self.chains.get(chain.name)
        if chain:
            return chain.invoke_query(query)
        else:
            raise ValueError(f"Chain with name {chain.name} not found")
