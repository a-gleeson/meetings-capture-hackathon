from abc import ABC, abstractmethod
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class Chunker(ABC):

    @abstractmethod
    def chunk_documents(self) -> List[Document]:
        raise NotImplementedError()


class TextChunker(Chunker):

    def __init__(self, chunk_size: int, overlap: int):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunker = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.overlap
        )

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        print(len(documents))
        docs = []
        for doc in documents:
            chunks = self.chunker.split_documents([doc])
            for chunk in chunks:
                new_doc = Document(
                    page_content=chunk.page_content, metadata={**doc.metadata}
                )
                docs.append(new_doc)

        print(len(docs))
        return docs
