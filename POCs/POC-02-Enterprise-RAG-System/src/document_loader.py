"""Document ingestion: load files from a directory, split into chunks."""

import os
from pathlib import Path
from typing import Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


# Supported file extensions and their loaders
SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf"}


def _read_text_file(file_path: Path) -> str:
    """Read a plain text or markdown file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def _read_pdf_file(file_path: Path) -> str:
    """Read a PDF file. Falls back gracefully if PyPDF is not installed."""
    try:
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(str(file_path))
        pages = loader.load()
        return "\n\n".join(page.page_content for page in pages)
    except ImportError:
        return f"[PDF support requires pypdf package: {file_path.name}]"


def load_documents(
    directory: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[Document]:
    """Load all supported files from a directory and split into chunks.

    Args:
        directory: Path to the directory containing documents.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between consecutive chunks.

    Returns:
        List of Document objects with metadata (source, chunk_index).
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise FileNotFoundError(f"Directory not found: {directory}")

    # Collect raw documents
    raw_docs: list[Document] = []
    for file_path in sorted(dir_path.rglob("*")):
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() == ".pdf":
            content = _read_pdf_file(file_path)
        else:
            content = _read_text_file(file_path)

        if content.strip():
            raw_docs.append(Document(
                page_content=content,
                metadata={"source": str(file_path.name)},
            ))

    if not raw_docs:
        return []

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[Document] = []
    for doc in raw_docs:
        splits = splitter.split_documents([doc])
        for i, chunk in enumerate(splits):
            chunk.metadata["chunk_index"] = i
            chunk.metadata["total_chunks"] = len(splits)
            chunks.append(chunk)

    return chunks


def get_supported_files(directory: str) -> list[str]:
    """List all supported files in a directory."""
    dir_path = Path(directory)
    if not dir_path.is_dir():
        return []
    return [
        f.name for f in sorted(dir_path.rglob("*"))
        if f.suffix.lower() in SUPPORTED_EXTENSIONS and f.is_file()
    ]
