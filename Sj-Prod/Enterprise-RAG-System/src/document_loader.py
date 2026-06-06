"""Document ingestion: load files from a directory, split into chunks."""

import logging
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

# Supported file extensions and their loaders
SUPPORTED_EXTENSIONS: set[str] = {".md", ".txt", ".pdf"}


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
        logger.warning("PDF support requires pypdf package; skipping %s", file_path.name)
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

        logger.info("Loading document: %s", file_path.name)

        if file_path.suffix.lower() == ".pdf":
            content = _read_pdf_file(file_path)
        else:
            content = _read_text_file(file_path)

        if content.strip():
            raw_docs.append(
                Document(
                    page_content=content,
                    metadata={"source": str(file_path.name)},
                )
            )

    if not raw_docs:
        logger.warning("No documents with content found in %s", directory)
        return []

    logger.info("Loaded %d raw documents from %s", len(raw_docs), directory)

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

    logger.info(
        "Split %d documents into %d chunks (chunk_size=%d, overlap=%d)",
        len(raw_docs),
        len(chunks),
        chunk_size,
        chunk_overlap,
    )
    return chunks


def get_supported_files(directory: str) -> list[str]:
    """List all supported files in a directory."""
    dir_path = Path(directory)
    if not dir_path.is_dir():
        return []
    return [
        f.name
        for f in sorted(dir_path.rglob("*"))
        if f.suffix.lower() in SUPPORTED_EXTENSIONS and f.is_file()
    ]
