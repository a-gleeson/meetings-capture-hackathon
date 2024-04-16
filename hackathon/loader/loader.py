from abc import ABC, abstractmethod
from io import BytesIO
from typing import Dict, List, Optional

import boto3
import pandas as pd
from langchain_core.documents import Document

from config.settings import PROJECT_PATH
from hackathon.loader.processors import ProcessorFactory


class Loader(ABC):
    @abstractmethod
    def load(self, file_name):
        """
        Args:
            file_name (str): name of the file to load
        """
        raise NotImplementedError()


class FileLoader(Loader):
    """
    Returns the system file path for the file_name which can be loaded.
    """

    def load(self, file_name: str) -> str:
        file_path = f"{PROJECT_PATH}/data/{file_name}"
        return file_path


class S3Loader(Loader):
    """
    S3 loader which loads files from s3.
    """

    def __init__(self, bucket: str) -> None:
        self.bucket = bucket
        self.s3_client = boto3.client("s3")

    def load(self, file_name: str) -> BytesIO:
        obj = self.s3_client.get_object(Bucket=self.bucket, Key=file_name)
        return BytesIO(obj["Body"].read())


def load_and_process_file(
    loader: Loader,
    file_name: str,
    source_column: Optional[str] = None,
    metadata_columns: Optional[List[str]] = None,
    content_columns: Optional[List[str]] = None,
) -> List[Document]:
    """
    This method takes a specific loader which controls where the file is loaded from and then
    takes a filename which is passed to a factory to chose which processor it needs and then
    load and process the data, The column config is used for processing the data.
    Args:
        loader (Loader): the loader which will be used to load the file
        file_path (str): name of file to process
    """
    processor = ProcessorFactory.get_processor(
        file_name, source_column, metadata_columns, content_columns
    )
    raw_data = loader.load(file_name)
    docs = processor.transform_to_docs(raw_data)
    return docs
