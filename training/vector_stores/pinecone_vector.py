"""
Pinecone Vector Store implementation for Vanna AI.

This module provides Pinecone integration as a vector database for Vanna AI,
following SOLID principles and the existing architecture patterns.
"""

import ast
import json
import os
import logging
import hashlib
from typing import List, Dict, Any, Optional
import pandas as pd
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI


class PineconeVectorStore:
    """
    Pinecone Vector Store for Vanna AI.
    
    Provides vector storage and retrieval capabilities using Pinecone service.
    Follows Single Responsibility Principle by focusing solely on vector operations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize Pinecone Vector Store.
        
        Args:
            config: Configuration dictionary containing Pinecone settings
            
        Raises:
            ValueError: If required configuration is missing
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Validate required configuration
        self._validate_config()
        
        # Initialize configuration with defaults
        self.api_key = self.config.get(
            "pinecone_api_key",
            os.getenv("PINECONE_API_KEY")
        )
        self.environment = self.config.get(
            "pinecone_environment",
            os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
        )
        self.dimensions = self.config.get("dimensions", 1536)  # OpenAI text-embedding-3-small dimensions
        self.embedding_model = self.config.get("embedding_model", "text-embedding-3-small")
        self.index_name = self.config.get("index_name", "vanna-index")
        self.n_results_ddl = self.config.get("n_results_ddl", self.config.get("n_results", 10))
        self.n_results_sql = self.config.get("n_results_sql", self.config.get("n_results", 10))
        self.n_results_documentation = self.config.get("n_results_documentation", self.config.get("n_results", 10))
        
        # Initialize Pinecone client
        self._initialize_pinecone()
        
        # Initialize OpenAI client for embeddings
        self._initialize_openai_client()
        
        # Create index if it doesn't exist
        self._ensure_index_exists()
        
        self.logger.info(f"Pinecone Vector Store initialized with index: {self.index_name}")
    
    def _validate_config(self) -> None:
        """Validate required configuration parameters."""
        api_key = self.config.get("pinecone_api_key", os.getenv("PINECONE_API_KEY"))
        
        if not api_key:
            raise ValueError(
                "Pinecone API key is required. Set 'pinecone_api_key' in config or "
                "PINECONE_API_KEY environment variable."
            )
    
    def _initialize_pinecone(self) -> None:
        """Initialize Pinecone client."""
        self.pc = Pinecone(api_key=self.api_key)
    
    def _initialize_openai_client(self) -> None:
        """Initialize OpenAI client for embeddings."""
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Please set it in your .env file."
            )
        
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.logger.info("Using OpenAI for embeddings")
    
    def _ensure_index_exists(self) -> None:
        """Create index if it doesn't exist."""
        try:
            # List existing indexes
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                self.logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimensions,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=self.environment
                    )
                )
                self.logger.info(f"Index '{self.index_name}' created successfully")
                # Wait for index to be ready
                import time
                max_wait = 60  # Maximum wait time in seconds
                wait_time = 0
                while wait_time < max_wait:
                    try:
                        indexes = [idx.name for idx in self.pc.list_indexes()]
                        if self.index_name in indexes:
                            break
                    except Exception:
                        pass
                    time.sleep(2)
                    wait_time += 2
            else:
                self.logger.info(f"Index '{self.index_name}' already exists")
            
            # Get index connection
            self.index = self.pc.Index(self.index_name)
            
        except Exception as e:
            self.logger.error(f"Error ensuring index exists: {e}")
            raise
    
    def _generate_deterministic_uuid(self, content: str) -> str:
        """Generate deterministic UUID for content."""
        return hashlib.md5(content.encode()).hexdigest()
    
    def add_ddl(self, ddl: str) -> str:
        """
        Add DDL to the vector store.
        
        Args:
            ddl: DDL statement to add
            
        Returns:
            str: Document ID
        """
        try:
            doc_id = self._generate_deterministic_uuid(ddl) + "-ddl"
            embedding = self.generate_embedding(ddl)
            
            # Prepare metadata
            metadata = {
                "document": ddl,
                "training_data_type": "ddl"
            }
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[{
                    "id": doc_id,
                    "values": embedding,
                    "metadata": metadata
                }]
            )
            
            self.logger.debug(f"Added DDL document with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            self.logger.error(f"Error adding DDL: {e}")
            raise
    
    def add_documentation(self, doc: str) -> str:
        """
        Add documentation to the vector store.
        
        Args:
            doc: Documentation text to add
            
        Returns:
            str: Document ID
        """
        try:
            doc_id = self._generate_deterministic_uuid(doc) + "-doc"
            embedding = self.generate_embedding(doc)
            
            # Prepare metadata
            metadata = {
                "document": doc,
                "training_data_type": "documentation"
            }
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[{
                    "id": doc_id,
                    "values": embedding,
                    "metadata": metadata
                }]
            )
            
            self.logger.debug(f"Added documentation document with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            self.logger.error(f"Error adding documentation: {e}")
            raise
    
    def add_question_sql(self, question: str, sql: str) -> str:
        """
        Add question-SQL pair to the vector store.
        
        Args:
            question: Natural language question
            sql: Corresponding SQL query
            
        Returns:
            str: Document ID
        """
        try:
            question_sql_json = json.dumps(
                {"question": question, "sql": sql},
                ensure_ascii=False
            )
            doc_id = self._generate_deterministic_uuid(question_sql_json) + "-sql"
            embedding = self.generate_embedding(question_sql_json)
            
            # Prepare metadata
            metadata = {
                "document": question_sql_json,
                "training_data_type": "sql",
                "question": question,
                "sql": sql
            }
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[{
                    "id": doc_id,
                    "values": embedding,
                    "metadata": metadata
                }]
            )
            
            self.logger.debug(f"Added SQL document with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            self.logger.error(f"Error adding question-SQL pair: {e}")
            raise
    
    def get_related_ddl(self, text: str, **kwargs) -> List[str]:
        """
        Get related DDL statements based on text similarity.
        
        Args:
            text: Query text
            
        Returns:
            List[str]: Related DDL statements
        """
        try:
            query_embedding = self.generate_embedding(text)
            
            # Query Pinecone with filter
            results = self.index.query(
                vector=query_embedding,
                top_k=self.n_results_ddl,
                include_metadata=True,
                filter={"training_data_type": {"$eq": "ddl"}}
            )
            
            ddl_list = []
            if results.matches:
                for match in results.matches:
                    if match.metadata and "document" in match.metadata:
                        ddl_list.append(match.metadata["document"])
            
            return ddl_list
            
        except Exception as e:
            self.logger.error(f"Error getting related DDL: {e}")
            return []
    
    def get_related_documentation(self, text: str, **kwargs) -> List[str]:
        """
        Get related documentation based on text similarity.
        
        Args:
            text: Query text
            
        Returns:
            List[str]: Related documentation
        """
        try:
            query_embedding = self.generate_embedding(text)
            
            # Query Pinecone with filter
            results = self.index.query(
                vector=query_embedding,
                top_k=self.n_results_documentation,
                include_metadata=True,
                filter={"training_data_type": {"$eq": "documentation"}}
            )
            
            doc_list = []
            if results.matches:
                for match in results.matches:
                    if match.metadata and "document" in match.metadata:
                        doc_list.append(match.metadata["document"])
            
            return doc_list
            
        except Exception as e:
            self.logger.error(f"Error getting related documentation: {e}")
            return []
    
    def get_similar_question_sql(self, question: str, **kwargs) -> List[Dict[str, str]]:
        """
        Get similar question-SQL pairs based on question similarity.
        
        Args:
            question: Query question
            
        Returns:
            List[Dict[str, str]]: Similar question-SQL pairs
        """
        try:
            query_embedding = self.generate_embedding(question)
            
            # Query Pinecone with filter
            results = self.index.query(
                vector=query_embedding,
                top_k=self.n_results_sql,
                include_metadata=True,
                filter={"training_data_type": {"$eq": "sql"}}
            )
            
            question_sql_pairs = []
            if results.matches:
                for match in results.matches:
                    if match.metadata:
                        # Try to get question and sql from metadata first
                        if "question" in match.metadata and "sql" in match.metadata:
                            question_sql_pairs.append({
                                "question": match.metadata["question"],
                                "sql": match.metadata["sql"]
                            })
                        elif "document" in match.metadata:
                            # Fallback to parsing JSON document
                            try:
                                doc_data = json.loads(match.metadata["document"])
                                question_sql_pairs.append(doc_data)
                            except (json.JSONDecodeError, TypeError):
                                pass
            
            return question_sql_pairs
            
        except Exception as e:
            self.logger.error(f"Error getting similar question-SQL pairs: {e}")
            return []
    
    def generate_embedding(self, data: str, **kwargs) -> List[float]:
        """
        Generate embedding for text data using OpenAI.
        
        Args:
            data: Text to generate embedding for
            **kwargs: Additional arguments (unused)
            
        Returns:
            List[float]: Embedding vector
        """
        try:
            response = self.openai_client.embeddings.create(
                input=data,
                model=self.embedding_model
            )
            return response.data[0].embedding
            
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            raise
    
    def get_training_data(self, **kwargs) -> pd.DataFrame:
        """
        Get all training data from the vector store.
        
        Returns:
            pd.DataFrame: Training data with columns [id, question, content, training_data_type]
        """
        try:
            all_data = []
            
            # Query with zero vector to get all vectors (fallback method)
            zero_vector = [0.0] * self.dimensions
            results = self.index.query(
                vector=zero_vector,
                top_k=10000,
                include_metadata=True
            )
            
            if results.matches:
                for match in results.matches:
                    if match.metadata:
                        training_type = match.metadata.get("training_data_type", "unknown")
                        document = match.metadata.get("document", "")
                        
                        # Process based on training data type
                        if training_type == "sql":
                            try:
                                sql_data = json.loads(document)
                                question = sql_data.get("question", "")
                                content = sql_data.get("sql", "")
                            except (json.JSONDecodeError, TypeError):
                                question = match.metadata.get("question", "")
                                content = match.metadata.get("sql", "")
                        else:
                            question = None
                            content = document
                        
                        all_data.append({
                            "id": match.id,
                            "question": question,
                            "content": content,
                            "training_data_type": training_type
                        })
            
            if not all_data:
                self.logger.info("No training data found in Pinecone index")
                return pd.DataFrame(columns=["id", "question", "content", "training_data_type"])
            
            self.logger.info(f"Successfully retrieved {len(all_data)} training records from Pinecone")
            df = pd.DataFrame(all_data)
            return df[["id", "question", "content", "training_data_type"]]
            
        except Exception as e:
            self.logger.error(f"Error getting training data: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return pd.DataFrame(columns=["id", "question", "content", "training_data_type"])
    
    def remove_training_data(self, id: str, **kwargs) -> bool:
        """
        Remove training data by ID.
        
        Args:
            id: Document ID to remove
            **kwargs: Additional arguments
            
        Returns:
            bool: True if removal was successful
        """
        try:
            self.index.delete(ids=[id])
            self.logger.debug(f"Removed document with ID: {id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing training data: {e}")
            return False

