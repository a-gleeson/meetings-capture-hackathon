import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.helpers import bulk

from config.logging import setup_logging
from config.settings import OPENSEARCH_URL

get_logger = setup_logging()
logger = get_logger(__name__)


class OpensearchClient:
    """
    Attributes:
        index_name (str): string name for the index where the data is stored
        endpoint_name (str): endpoint name for the opensearch aws endpoint defaults to None
        region (str): string of the aws region that opensearch is in default to None
    """

    def __init__(self, index_name, endpoint_name=None, region=None) -> None:
        self.http_auth = None
        self.client = None
        self.endpoint_name = endpoint_name
        self.index_name = index_name
        self.opensearch_endpoint = self._get_opensearch_endpoint(endpoint_name, region)
        self.client = self.get_client()

    def get_client(self):
        """
        Gets and returns the pensearch client if it is not already set.
        if http_auth is set, set up the endpoint in local config (verify certs set to False and port 9002)
        else set it to port 443 and verify certs.
        """

        if not self.client:
            if self.http_auth:
                return OpenSearch(
                    hosts=[{"host": self.opensearch_endpoint, "port": 9002}],
                    index_name=self.index_name,
                    http_auth=self.http_auth,
                    use_ssl=True,
                    verify_certs=False,
                    connection_class=RequestsHttpConnection,
                    timeout=30,
                )
            else:
                return OpenSearch(
                    hosts=[{"host": self.opensearch_endpoint, "port": 443}],
                    index_name=self.index_name,
                    use_ssl=True,
                    verify_certs=True,
                    connection_class=RequestsHttpConnection,
                    timeout=30,
                )
        else:
            return self.client

    def _get_opensearch_endpoint(self, endpoint_name, region=None):
        """
        Returns Endpoint for opensearch, returns Config param OPENSEARCH_URL (used for local set up) if set and
        sets http_auth,
        Otherwise uses boto3 client to get endpoint using endpoint_name and region.
        Args:
            endpoint_name (str): aws endpoint name for opensearch can be none if local set up
            region (str): AWS region for opensearch cluster defaults to None
        """
        if OPENSEARCH_URL:
            self.http_auth = ("admin", "admin")
            return OPENSEARCH_URL
        client = boto3.client("es", region_name=region)
        response = client.describe_elasticsearch_domain(DomainName=endpoint_name)
        return response["DomainStatus"]["Endpoints"]["vpc"]

    def _put_bulk_in_opensearch(self, docs):
        """
        Deprecated!!!
        Currently unused but using opensearch API to store documents into opensearch
        """
        logger.info(f"Putting {len(docs)} documents in OpenSearch")
        success, failed = bulk(self.client, docs)
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
        return self.client.indices.exists(index=index_name)

    def _create_index(self, index_name=None):
        """
        Deprecated!!!
        Used in direct opensearch interaction to create the index, OpenSearchVectorSearch does this automatically
        when storing data
        """
        if not index_name:
            index_name = self.index_name
        settings = {
            "settings": {"index": {"knn": True, "knn.space_type": "cosinesimil"}}
        }
        response = self.client.indices.create(index=index_name, body=settings)
        return bool(response["acknowledged"])

    def _create_index_mapping(self, index_name=None):
        """
        Deprecated!!! Mappings not workings for vector sizes creatd from embeddings.
        Used in direct opensearch interaction to create the index mapping, OpenSearchVectorSearch does this automatically
        when storing data
        """
        if not index_name:
            index_name = self.index_name
        response = self.client.indices.put_mapping(
            index=index_name,
            body={
                "properties": {
                    "vector_field": {"type": "knn_vector", "dimension": 1536},
                    "text": {"type": "keyword"},
                }
            },
        )
        return bool(response["acknowledged"])

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
        logger.info("Trying to delete index %s", index_name)
        try:
            response = self.client.indices.delete(index=index_name)
            logger.info("Index %s deleted", response)
            return response["acknowledged"]
        except Exception:
            logger.error("Index %s not found, nothing to delete", index_name)
            return True
