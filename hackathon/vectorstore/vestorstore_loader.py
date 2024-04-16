from config.settings import S3_LOADER_FILE_NAME
from hackathon.constants.constants import CONTENT_COLUMNS, METADATA_COLUMNS
from hackathon.loader.chunker import Chunker
from hackathon.loader.loader import Loader, load_and_process_file
from hackathon.vectorstore.vectorstore import VectorStoreClient


class VectorstoreLoader:
    def __init__(
        self,
        vectorstore_client: VectorStoreClient,
        loader: Loader,
        chunker: Chunker = None,
    ) -> None:
        self.chunker = chunker
        self.vs_client = vectorstore_client
        self.loader = loader

    def data_store_exists(self, **kwargs) -> bool:
        return self.vs_client.check_data_exists(**kwargs)

    def fresh_data_load(self, source_file=None, **kwargs):
        if self.data_store_exists(**kwargs):
            return None
        return self._load_and_store_data(source_file)

    def recreate_data_load(self, source_file=None, **kwargs):
        if self.data_store_exists(**kwargs):
            self.vs_client.delete_data_store(**kwargs)
        return self._load_and_store_data(source_file)

    def _create_data_store(self, **kwargs):
        return self.vs_client.create_store(**kwargs)

    def _load_and_store_data(self, source_file=S3_LOADER_FILE_NAME, **kwargs):
        if not self.data_store_exists(**kwargs):
            self._create_data_store(**kwargs)
        loaded_documents = load_and_process_file(
            self.loader,
            source_file,
            metadata_columns=METADATA_COLUMNS,
            content_columns=CONTENT_COLUMNS,
        )
        if self.chunker:
            chunked_documents = self.chunker.chunk_documents(loaded_documents)
            return self.vs_client.store_data(chunked_documents)
        else:
            return self.vs_client.store_data(loaded_documents)
