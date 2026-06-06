"""
RAG Pipeline Implementation
Retrieval-Augmented Generation for data documentation
"""
import os
import logging
from typing import List, Dict, Any, Optional
from langchain.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone, Chroma
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import pinecone

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Retrieval-Augmented Generation Pipeline"""
    
    def __init__(
        self,
        vector_store_type: str = "pinecone",
        embedding_model: str = "openai",
        llm_provider: str = "openai"
    ):
        """
        Initialize RAG pipeline
        
        Args:
            vector_store_type: Type of vector store ("pinecone" or "chroma")
            embedding_model: Embedding model ("openai" or "huggingface")
            llm_provider: LLM provider ("openai" or "huggingface")
        """
        self.vector_store_type = vector_store_type
        self.embedding_model = embedding_model
        self.llm_provider = llm_provider
        
        # Initialize embeddings
        self.embeddings = self._initialize_embeddings()
        
        # Initialize vector store
        self.vector_store = None
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Initialize QA chain
        self.qa_chain = None
    
    def _initialize_embeddings(self):
        """Initialize embedding model"""
        if self.embedding_model == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            return OpenAIEmbeddings(openai_api_key=api_key)
        else:
            # Use HuggingFace embeddings
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
    
    def _initialize_llm(self):
        """Initialize LLM"""
        if self.llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            return OpenAI(
                openai_api_key=api_key,
                temperature=0.7,
                model_name="gpt-3.5-turbo"
            )
        else:
            # Use HuggingFace models (requires transformers library)
            from langchain.llms import HuggingFacePipeline
            # This would require additional setup
            raise NotImplementedError("HuggingFace LLM not yet implemented")
    
    def load_documents(self, data_dir: str, file_type: str = "pdf") -> List:
        """
        Load documents from directory
        
        Args:
            data_dir: Directory containing documents
            file_type: Type of files to load ("pdf", "txt", "all")
            
        Returns:
            List of loaded documents
        """
        logger.info(f"Loading documents from {data_dir}...")
        
        if file_type == "pdf":
            loader = DirectoryLoader(
                data_dir,
                glob="**/*.pdf",
                loader_cls=PyPDFLoader
            )
        elif file_type == "txt":
            loader = DirectoryLoader(
                data_dir,
                glob="**/*.txt",
                loader_cls=TextLoader
            )
        else:
            # Load all supported types
            loaders = []
            if os.path.exists(data_dir):
                for file in os.listdir(data_dir):
                    if file.endswith(".pdf"):
                        loaders.append(PyPDFLoader(os.path.join(data_dir, file)))
                    elif file.endswith(".txt"):
                        loaders.append(TextLoader(os.path.join(data_dir, file)))
            
            documents = []
            for loader in loaders:
                documents.extend(loader.load())
            return documents
        
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} documents")
        
        return documents
    
    def split_documents(
        self,
        documents: List,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List:
        """
        Split documents into chunks
        
        Args:
            documents: List of documents
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of document chunks
        """
        logger.info("Splitting documents into chunks...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks")
        
        return chunks
    
    def create_vector_store(
        self,
        documents: List,
        index_name: str = "rag-index"
    ):
        """
        Create vector store from documents
        
        Args:
            documents: List of document chunks
            index_name: Name of the vector index
        """
        logger.info(f"Creating vector store: {self.vector_store_type}...")
        
        if self.vector_store_type == "pinecone":
            # Initialize Pinecone
            api_key = os.getenv("PINECONE_API_KEY")
            environment = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
            
            if not api_key:
                raise ValueError("PINECONE_API_KEY not found in environment")
            
            pinecone.init(api_key=api_key, environment=environment)
            
            # Create or get index
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=index_name,
                    dimension=1536,  # OpenAI embedding dimension
                    metric="cosine"
                )
            
            # Create vector store
            self.vector_store = Pinecone.from_documents(
                documents,
                self.embeddings,
                index_name=index_name
            )
        else:
            # Use Chroma (local)
            persist_directory = "./chroma_db"
            self.vector_store = Chroma.from_documents(
                documents,
                self.embeddings,
                persist_directory=persist_directory
            )
        
        logger.info("Vector store created successfully!")
    
    def create_qa_chain(self, k: int = 4):
        """
        Create QA chain with retrieval
        
        Args:
            k: Number of documents to retrieve
        """
        logger.info("Creating QA chain...")
        
        # Custom prompt template
        prompt_template = """Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.

        Context: {context}

        Question: {question}

        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create retriever
        retriever = self.vector_store.as_retriever(
            search_kwargs={"k": k}
        )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        logger.info("QA chain created successfully!")
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG system
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and source documents
        """
        if self.qa_chain is None:
            raise ValueError("QA chain not initialized. Call create_qa_chain() first.")
        
        logger.info(f"Processing query: {question}")
        
        result = self.qa_chain({"query": question})
        
        return {
            "answer": result["result"],
            "source_documents": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in result.get("source_documents", [])
            ]
        }
    
    def build_pipeline(
        self,
        data_dir: str,
        index_name: str = "rag-index",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Build complete RAG pipeline
        
        Args:
            data_dir: Directory containing documents
            index_name: Name of the vector index
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
        """
        # Load documents
        documents = self.load_documents(data_dir)
        
        # Split documents
        chunks = self.split_documents(documents, chunk_size, chunk_overlap)
        
        # Create vector store
        self.create_vector_store(chunks, index_name)
        
        # Create QA chain
        self.create_qa_chain()
        
        logger.info("RAG pipeline built successfully!")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Initialize pipeline
    rag = RAGPipeline(
        vector_store_type="chroma",  # Use Chroma for local testing
        embedding_model="huggingface",
        llm_provider="openai"
    )
    
    # Build pipeline
    data_dir = "data/documents"
    if os.path.exists(data_dir):
        rag.build_pipeline(data_dir)
        
        # Test query
        result = rag.query("What is the main topic of the documents?")
        print(f"Answer: {result['answer']}")
        print(f"Sources: {len(result['source_documents'])} documents")
    else:
        logger.warning(f"Data directory {data_dir} not found. Please add documents.")

