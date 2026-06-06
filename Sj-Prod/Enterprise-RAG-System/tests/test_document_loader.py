"""Tests for the document loader module."""

import pytest
from pathlib import Path

from src.document_loader import (
    SUPPORTED_EXTENSIONS,
    _read_text_file,
    get_supported_files,
    load_documents,
)


class TestReadTextFile:
    """Tests for reading individual text files."""

    def test_read_markdown_file(self, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text("# Hello\n\nWorld")
        content = _read_text_file(md_file)
        assert content == "# Hello\n\nWorld"

    def test_read_txt_file(self, tmp_path):
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Plain text content")
        content = _read_text_file(txt_file)
        assert content == "Plain text content"

    def test_read_empty_file(self, tmp_path):
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("")
        content = _read_text_file(empty_file)
        assert content == ""

    def test_read_file_with_utf8(self, tmp_path):
        utf8_file = tmp_path / "unicode.md"
        utf8_file.write_text("Caf\u00e9 and na\u00efve")
        content = _read_text_file(utf8_file)
        assert "Caf\u00e9" in content


class TestLoadDocuments:
    """Tests for loading and chunking documents from a directory."""

    def test_load_single_markdown(self, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nSome content for testing.")
        chunks = load_documents(str(tmp_path))
        assert len(chunks) >= 1
        assert chunks[0].metadata["source"] == "test.md"

    def test_load_multiple_files(self, sample_docs_dir):
        chunks = load_documents(str(sample_docs_dir))
        assert len(chunks) >= 2
        sources = {c.metadata["source"] for c in chunks}
        assert "docker.md" in sources
        assert "kubernetes.md" in sources

    def test_chunk_metadata_has_chunk_index(self, sample_docs_dir):
        chunks = load_documents(str(sample_docs_dir))
        for chunk in chunks:
            assert "chunk_index" in chunk.metadata
            assert "total_chunks" in chunk.metadata
            assert isinstance(chunk.metadata["chunk_index"], int)

    def test_chunking_respects_size(self, tmp_path):
        md_file = tmp_path / "long.md"
        # Create a file with enough content to produce multiple chunks
        md_file.write_text("This is a sentence. " * 200)
        chunks = load_documents(str(tmp_path), chunk_size=500, chunk_overlap=50)
        assert len(chunks) > 1
        for chunk in chunks:
            # Allow some margin for chunk boundary splitting
            assert len(chunk.page_content) <= 600

    def test_empty_file_produces_no_chunks(self, empty_docs_dir):
        chunks = load_documents(str(empty_docs_dir))
        assert chunks == []

    def test_whitespace_only_file_produces_no_chunks(self, tmp_path):
        ws_file = tmp_path / "whitespace.md"
        ws_file.write_text("   \n\n   \t  \n  ")
        chunks = load_documents(str(tmp_path))
        assert chunks == []

    def test_nonexistent_directory_raises(self):
        with pytest.raises(FileNotFoundError):
            load_documents("/nonexistent/path/to/docs")

    def test_unsupported_files_ignored(self, mixed_docs_dir):
        chunks = load_documents(str(mixed_docs_dir))
        sources = {c.metadata["source"] for c in chunks}
        assert "readme.md" in sources
        assert "notes.txt" in sources
        assert "image.png" not in sources
        assert "script.py" not in sources


class TestFileTypeDetection:
    """Tests for supported file type detection."""

    def test_supported_extensions_include_md(self):
        assert ".md" in SUPPORTED_EXTENSIONS

    def test_supported_extensions_include_txt(self):
        assert ".txt" in SUPPORTED_EXTENSIONS

    def test_supported_extensions_include_pdf(self):
        assert ".pdf" in SUPPORTED_EXTENSIONS

    def test_get_supported_files(self, mixed_docs_dir):
        files = get_supported_files(str(mixed_docs_dir))
        assert "readme.md" in files
        assert "notes.txt" in files
        assert "image.png" not in files
        assert "script.py" not in files

    def test_get_supported_files_nonexistent_dir(self):
        files = get_supported_files("/nonexistent/path")
        assert files == []

    def test_get_supported_files_empty_dir(self, tmp_path):
        files = get_supported_files(str(tmp_path))
        assert files == []
