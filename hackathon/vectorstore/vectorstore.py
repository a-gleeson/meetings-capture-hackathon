from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from langchain.vectorstores import Chroma, OpenSearchVectorSearch
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStoreRetriever
from opensearchpy.helpers import bulk

from config.logging import setup_logging
from config.settings import OPENSEARCH_BATCH_SIZE
from hackathon.vectorstore.opensearch import OpensearchClient

get_logger = setup_logging()
logger = get_logger(__name__)


class VectorStore(ABC):
    """
    VectorStore class in control of searching an exisiting vector store.
    """

    @abstractmethod
    def store_data(self, documents: List[Document]):
        raise NotImplementedError()

    @abstractmethod
    def retrieve_data(self, query: str):
        raise NotImplementedError()

    @abstractmethod
    def get_as_retriever(self, search_kwargs: int = 2):
        raise NotImplementedError()


class ChromaStore(VectorStore):
    """
    https://api.python.langchain.com/en/latest/vectorstores/langchain_community.vectorstores.chroma.Chroma.html?highlight=chroma#langchain_community.vectorstores.chroma.Chroma
    """

    def __init__(
        self, embedding_function: Embeddings, collection_name: str = ""
    ) -> None:
        print(f"persist_directory name: {collection_name}")
        self.vectorstore = Chroma(
            embedding_function=embedding_function,
            persist_directory=collection_name,
            collection_name=collection_name,
        )

    def store_data(self, documents: List[Document]):
        self._store_documents(documents)

    def _store_documents(self, documents: List[Document]):
        self.vectorstore.add_documents(documents)

    def retrieve_data(self, query: str):
        return self.vectorstore.similarity_search(query, k=20)

    def get_as_retriever(self, search_kwargs: int = 2) -> VectorStoreRetriever:
        return self.vectorstore.as_retriever(search_kwargs={"k": search_kwargs})

    def get_documents(self, limit: Optional[int] = None):
        return self.vectorstore.get(limit=limit)

    def search_with_score(self, query: str):
        return self.vectorstore.similarity_search_with_relevance_scores(query, k=100)

    def similarity_search_with_filter(
        self, query: str, filter: Optional[Dict[str, str]]
    ):
        return self.vectorstore.similarity_search(query, k=10, filter=filter)


class OpenSearchStore(VectorStore):
    """

    Attributes:
        embedding_function (Embeddings): an embeddings function which will be used to embed the documents to vectors
        index_name (str): string name for the index where the vectors are stored
        client (OpensearchClient): Opensearch client
    """

    def __init__(
        self,
        embedding_function: Embeddings,
        index_name,
        client: OpensearchClient,
    ):
        self.vectorstore = None
        self.embedding_function: Embeddings = embedding_function
        self.index_name = index_name
        self.vectorstore = OpenSearchVectorSearch(
            client=client.client,
            index_name=self.index_name,
            embedding_function=embedding_function,
            opensearch_url=client.opensearch_endpoint,
            # connection_class=RequestsHttpConnection,
            # timeout=30,
            # port=443,
        )

    def _split_into_batches(self, docs):
        """Split the document list into batches."""
        for i in range(0, len(docs), OPENSEARCH_BATCH_SIZE):
            yield docs[i : i + OPENSEARCH_BATCH_SIZE]

    def store_data(self, documents: List[Document]):
        raise NotImplementedError

    def retrieve_data_with_score(self, query):
        """
        Similarity search which returns values with score attachmend with up to 10 results
        """
        return self.vectorstore.similarity_search_with_score(query, k=10)

    def retrieve_data(
        self,
        query: str,
        search_type: str,
        space_type: str,
        pre_filter,
        k: int = 5,
    ):
        """
        Similarity search which returns values with score attachmend with up to k results,
        with search_type and space_type set and an applied pre_filter on the metadata.
        Args:
            query (str): query to search vector documents with
            search_type (str):
            space_type (str):
            pre_filter (object): filter to apply to the metadata results in the vector store
            k (int) integer for number of results to return defaults to 5
        """
        return self.vectorstore.similarity_search(
            query=query,
            search_type=search_type,
            space_type=space_type,
            pre_filter=pre_filter,
            k=k,
        )

    def get_as_retriever(self, search_kwargs: int = 2):
        """
        Returns a retriver that can be queried.
        Args:
            search_kwargs (int): integer for how many results to return in retriever calls
        """
        return self.vectorstore.as_retriever(search_kwargs={"k": search_kwargs})

    def get_documents(self, limit: Optional[int] = None):
        """
        Returns documents from vectorstore up to limit values
        Args:
            limit (Optional(int)): limit for the amount of documents to return defaults to None
        """
        return self.vectorstore.get(limit=limit)

    def retrieve_data_with_relevance_scores(self, query):
        return self.vectorstore.similarity_search_with_relevance_scores(query, k=10)


class VectorStoreClient(ABC):
    """
    Vector Store Client class charged with loading data into the vector store.
    """

    @abstractmethod
    def store_data(self, documents):
        raise NotImplementedError()

    @abstractmethod
    def check_data_exists(self, store=None):
        raise NotImplementedError()

    @abstractmethod
    def create_store(self, store=None):
        raise NotImplementedError()

    @abstractmethod
    def delete_data_store(self, store=None):
        raise NotImplementedError()


class ChromaClient(VectorStoreClient):

    def __init__(self, embedding_function: Embeddings, name: str = "") -> None:
        self.embedding_function: Embeddings = embedding_function
        self.name = name
        self.client = Chroma(
            embedding_function=self.embedding_function,
            persist_directory=self.name,
            collection_name=self.name,
        )

    def store_data(self, documents):
        logger.info("storing docs %s in Chroma", len(documents))
        response = self.client.add_documents(documents)
        logger.info("Put docs %s in Chroma with response %s", len(documents), response)
        self.client.persist()
        return response

    def check_data_exists(self, store=None):
        import os

        if not os.path.isdir(self.name):
            return False

        for entry in os.listdir(self.name):
            path = os.path.join(self.name, entry)
            if os.path.isdir(path):
                return True
        return False

    def create_store(self, store=None):
        if store:
            collection = store
        else:
            collection = self.name
        self.client = Chroma(
            embedding_function=self.embedding_function,
            persist_directory=collection,
            collection_name=collection,
        )
        return self.client

    def delete_data_store(self, store=None):
        try:
            self.client.delete_collection()
            # shutil.rmtree(self.name)
        except Exception as error:
            print(f"Error: {error}")


class OpensearchClientStore(VectorStoreClient):
    """
    Attributes:
        embedding_function (Embeddings): an embeddings function which will be used to embed the documents to vectors
        index_name (str): string name for the index where the vectors are stored
        client (OpensearchClient): Opensearch client
    """

    def __init__(
        self,
        embedding_function,
        index_name,
        client: OpensearchClient,
    ) -> None:

        self.embedding_function: Embeddings = embedding_function
        self.index_name = index_name
        self.vectorstore = OpenSearchVectorSearch(
            client=client.client,
            index_name=self.index_name,
            embedding_function=self.embedding_function,
            opensearch_url=client.opensearch_endpoint,
            # connection_class=RequestsHttpConnection,
            # timeout=30,
            # port=443,
        )

    def _split_into_batches(self, docs):
        """Split the document list into batches."""
        for i in range(0, len(docs), OPENSEARCH_BATCH_SIZE):
            logger.info(f"Batch of {i} to {i +OPENSEARCH_BATCH_SIZE} ...")
            yield docs[i : i + OPENSEARCH_BATCH_SIZE]

    def store_data(self, documents: List[Document]):
        """
        Stores data into opensearch, data is stored in batches and embedded as ingested.
        Args:
            Documents (list[Document]): list of documents to store into opensearch.
        """
        logger.info(f"Starting Opensearch ingestion of {len(documents)} documents")
        for batch in self._split_into_batches(documents):
            try:
                response = self.vectorstore.add_documents(batch)
            except Exception as e:
                # TODO what if a batch fails
                raise e
        logger.info("Finished Opensearch ingestion")

    def _put_bulk_in_opensearch(self, docs):
        """
        Deprecated!!!
        Currently unused but using opensearch API to store documents into opensearch
        """
        logger.info(f"Putting {len(docs)} documents in OpenSearch")
        success, failed = bulk(self.vectorstore.client, docs)
        return success, failed

    def check_data_exists(self, store=None):
        """
        Checks if the index exists in the store,
        Args:
            store (str): check specific store or defaults to none and using default index_name set up in init
        """
        return self._check_index(store)

    def _check_index(self, index_name=None):
        """
        Checks if the index exists in the store. interacts with Opensearch client directly.
        Args:
            index_name (str): check specific index_name or defaults to none and uses default index_name set up in init
        """
        if not index_name:
            index_name = self.index_name
        return self.vectorstore.client.indices.exists(index=index_name)

    def create_store(self, store=None):
        raise NotImplementedError

    def delete_data_store(self, store=None):
        return self._delete_opensearch_index(store)

    def _delete_opensearch_index(self, index_name=None):
        """
        Deletes the index created in opensearch, by interacting directly with opensearch client.
        Args:
            index_name (str): index to delete defaults to none and uses value in init
        """
        if not index_name:
            index_name = self.index_name
        logger.info(f"Trying to delete index {index_name}")
        try:
            response = self.vectorstore.client.indices.delete(index=index_name)
            logger.info(f"Index {response} deleted")
            return response["acknowledged"]
        except Exception:
            logger.error(f"Index {index_name} not found, nothing to delete")
            return True
