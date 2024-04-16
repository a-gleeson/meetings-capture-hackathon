from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import pandas as pd
from langchain_core.documents import Document


class Processor(ABC):
    """
    A class used for processing loaded files into Langchain
    documents generally via panadas as an intermediary.

    Attributes:
        source_column (Optional[str]): Unused currently an old paramater
        metadata_columns (Optional[List[str]]): Columns that will be set in the metadata
        content_columns (Optional[List[str]]): Columns which will be joined and formated into the document content
    """

    def __init__(
        self,
        source_column: Optional[str] = None,
        metadata_columns: Optional[List[str]] = None,
        content_columns: Optional[List[str]] = None,
    ):
        self.source_column = source_column
        self.metadata_columns = metadata_columns
        self.content_columns = content_columns

    @abstractmethod
    def transform_to_docs(self, raw_data) -> pd:
        """
        Args:
            raw_data (): raw file data to read
        """
        raise NotImplementedError()

    def _dataframe_process(self, df) -> List[Document]:
        """
        Processes a dataframe of the data into a list of langchain document.
        It creates the document content and it's metadata from each row in the dataframe.
        Args:
            df (pandas): a dataframe of the data.
        """
        df["content"] = df.apply(
            lambda row: "\n".join(
                [str(row[col]).strip() for col in self.content_columns]
            ),
            axis=1,
        )
        if self.metadata_columns:
            df["metadata"] = df.apply(self._process_metadata, axis=1)
        else:
            df["metadata"] = {}

        df["metadata"] = df["metadata"].apply(lambda x: None if pd.isna(x) else x)

        docs = df.apply(
            lambda row: Document(page_content=row["content"], metadata=row["metadata"]),
            axis=1,
        ).tolist()

        # TODO re-add source column setting

        return docs

    def _process_metadata(self, row):
        """
        Sets the values of metadata ensuring it's type so it can be filterd on.
        Args:
            row (): a row of data
        """
        metadata = {}
        for col in self.metadata_columns:
            value = row[col]
            if isinstance(value, int):
                metadata[col] = int(value)
            elif isinstance(value, float):
                metadata[col] = float(value)
            elif isinstance(value, list):
                metadata[col] = list(value)
            else:
                metadata[col] = str(value)
        return metadata


class CSVProcessor(Processor):
    def transform_to_docs(self, raw_data) -> List[Document]:
        """
        Args:
            raw_data (): raw csv data to read
        """
        df = pd.read_csv(raw_data)
        return self._dataframe_process(df)


class ParquetProcessor(Processor):
    def transform_to_docs(self, raw_data) -> List[Document]:
        """
        Args:
            raw_data (): raw parquet data to read
        """
        df = pd.read_parquet(raw_data)
        return self._dataframe_process(df)


class ProcessorFactory:
    """
    Factory class to get a processor dependant on the file type.
    """

    @staticmethod
    def get_processor(
        file_path: str,
        source_column: Optional[str] = None,
        metadata_columns: Optional[List[str]] = None,
        content_columns: Optional[List[str]] = None,
    ):
        """
        Args:
            file_path (str): File name and path that will be processed
        Raises:
            ValueError: when the file type is not got a supportted processor
        """
        extension = file_path.split(".")[-1].lower()
        if extension == "csv":
            return CSVProcessor(source_column, metadata_columns, content_columns)
        elif extension == "parquet":
            return ParquetProcessor(source_column, metadata_columns, content_columns)
        else:
            ValueError(f"File type {extension} does not have a supported processor")
