"""
Custom Vanna AI implementation for Water Utility Data.

This class integrates OpenAI GPT-4o, Pinecone vector store, and SQLite database
to enable natural language to SQL queries for water utility financial and operational data.
"""

import os
import logging
import time
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List
from typing import Any as AnyType

from training.core.openai_chat import OpenAI_Chat
from openai import OpenAI
from training.vector_stores.pinecone_vector import PineconeVectorStore
from services.sql_prompt_service import SQLPromptService


class MyVanna(PineconeVectorStore, OpenAI_Chat):
    """
    Custom Vanna class using OpenAI and Pinecone for Water Utility Data.
    
    This class combines vector storage (Pinecone) with LLM capabilities (OpenAI)
    to enable natural language to SQL conversion for water utility data.
    """
    
    def __init__(self, config=None):
        """
        Initialize MyVanna instance.
        
        Args:
            config: Optional configuration dictionary
        """
        # Initialize loggers
        self.api_logger = logging.getLogger('vanna.api')
        self.vector_logger = logging.getLogger('vanna.vector')
        self.sql_logger = logging.getLogger('vanna.sql')
        
        # Initialize Pinecone for vector storage
        pinecone_config = {
            'pinecone_api_key': os.getenv('PINECONE_API_KEY'),
            'pinecone_environment': os.getenv('PINECONE_ENVIRONMENT', 'us-east-1'),
            'index_name': os.getenv('PINECONE_INDEX_NAME', 'aquasentinel-index'),
            'dimensions': 1536,  # OpenAI text-embedding-3-small dimensions
            'embedding_model': 'text-embedding-3-small',
            'n_results': 10
        }
        if config:
            pinecone_config.update(config)
            
        self.api_logger.info(f"Initializing Pinecone with config: {pinecone_config['index_name']}")
        PineconeVectorStore.__init__(self, config=pinecone_config)
        
        # Initialize OpenAI client
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Please set it in your .env file."
            )
        
        openai_client = OpenAI(api_key=openai_api_key)
        
        self.api_logger.info("Initializing OpenAI client")
        # Initialize OpenAI Chat with OpenAI client
        OpenAI_Chat.__init__(self, client=openai_client, config=config)

        # Configure SQLite connection using Vanna helper
        sqlite_env_path = os.getenv('SQLITE_DB_PATH', 'database/water_data.db')
        project_root = Path(__file__).resolve().parent.parent
        sqlite_path = Path(sqlite_env_path)
        if not sqlite_path.is_absolute():
            sqlite_path = (project_root / sqlite_path).resolve()

        if not sqlite_path.exists():
            raise FileNotFoundError(
                f"SQLite database not found at: {sqlite_path}. "
                "Please ensure database/csv_ingestion.py has been run."
            )

        self.api_logger.info(f"Connecting to SQLite database at {sqlite_path}")
        self.connect_to_sqlite(str(sqlite_path))
        
        # Flag to track response type for Flask integration
        self._last_response_type = 'sql'
        
        # Initialize custom SQL prompt service
        self.api_logger.info("Initializing SQLPromptService...")
        self.sql_prompt_service = SQLPromptService(
            dialect="SQLite",
            max_tokens=14000,
            expertise_label="AquaSentinel SQLite expert"
        )
        self.api_logger.info("SQLPromptService initialized successfully")
        
        self.api_logger.info("MyVanna instance initialized successfully")
    
    def get_related_ddl(self, question: str, **kwargs) -> List[str]:
        """
        Override to add comprehensive logging for DDL retrieval from vector database.
        """
        start_time = time.time()
        self.vector_logger.info(f"Starting DDL retrieval for question: '{question[:100]}...'")
        
        try:
            result = super().get_related_ddl(question, **kwargs)
            duration = time.time() - start_time
            
            self.vector_logger.info(f"DDL retrieval completed in {duration:.2f}s")
            self.vector_logger.info(f"Retrieved DDL content length: {len(result) if result else 0} characters")
            
            if result:
                self.vector_logger.info(f"DDL content preview: {result[:200]}...")
            else:
                self.vector_logger.warning("No DDL content retrieved from vector database")
                
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.vector_logger.error(f"DDL retrieval failed after {duration:.2f}s: {str(e)}")
            raise
    
    def get_related_documentation(self, question: str, **kwargs) -> List[str]:
        """
        Override to add comprehensive logging for documentation retrieval from vector database.
        """
        start_time = time.time()
        self.vector_logger.info(f"Starting documentation retrieval for question: '{question[:100]}...'")
        
        try:
            result = super().get_related_documentation(question, **kwargs)
            duration = time.time() - start_time
            
            self.vector_logger.info(f"Documentation retrieval completed in {duration:.2f}s")
            self.vector_logger.info(f"Retrieved documentation content length: {len(result) if result else 0} characters")
            
            if result:
                self.vector_logger.info(f"Documentation content preview: {result[:200]}...")
            else:
                self.vector_logger.warning("No documentation content retrieved from vector database")
                
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.vector_logger.error(f"Documentation retrieval failed after {duration:.2f}s: {str(e)}")
            raise
    
    def get_sql_prompt(
        self,
        initial_prompt: Optional[str],
        question: str,
        question_sql_list: list,
        ddl_list: list,
        doc_list: list,
        **kwargs
    ):
        """
        Override get_sql_prompt to leverage SQLPromptService for full control.
        """
        self.sql_logger.info("=== SQLPromptService CALLED ===")
        self.sql_logger.info(f"Question: '{question[:100]}{'...' if len(question) > 100 else ''}'")
        self.sql_logger.info(f"Context provided: {len(ddl_list)} DDL statements, {len(doc_list)} documentation items, {len(question_sql_list)} question-SQL examples")
        
        self.sql_logger.info("Calling SQLPromptService.build_sql_prompt()...")
        
        result = self.sql_prompt_service.build_sql_prompt(
            question=question,
            ddl_list=ddl_list,
            doc_list=doc_list,
            question_sql_list=question_sql_list,
            initial_prompt=initial_prompt,
            user_message_func=self.user_message,
            assistant_message_func=self.assistant_message,
            system_message_func=self.system_message
        )
        
        self.sql_logger.info(f"SQLPromptService.build_sql_prompt() completed. Returned {len(result)} messages")
        self.sql_logger.info("=== SQLPromptService CALL COMPLETE ===")
        
        return result
    
    def get_similar_question_sql(self, question: str, **kwargs) -> List[Dict[str, str]]:
        """
        Override to add comprehensive logging for similar question SQL retrieval.
        """
        start_time = time.time()
        self.vector_logger.info(f"Starting similar question SQL retrieval for: '{question[:100]}...'")
        
        try:
            result = super().get_similar_question_sql(question, **kwargs)
            duration = time.time() - start_time
            
            self.vector_logger.info(f"Similar question SQL retrieval completed in {duration:.2f}s")
            self.vector_logger.info(f"Retrieved {len(result)} similar question-SQL pairs")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.vector_logger.error(f"Similar question SQL retrieval failed after {duration:.2f}s: {str(e)}")
            raise
    
    def generate_sql(self, question: str, allow_llm_to_see_data: bool = True, **kwargs) -> str:
        """
        Override generate_sql to ensure allow_llm_to_see_data defaults to True.
        This ensures the LLM can always see data for database introspection.
        
        Args:
            question: Natural language question
            allow_llm_to_see_data: Whether to allow LLM to see data (defaults to True)
            **kwargs: Additional arguments
            
        Returns:
            str: Generated SQL query
        """
        # Always allow LLM to see data for this implementation
        # This is safe because we're using a read-only SQLite database
        self.api_logger.info(f"Generating SQL for question: '{question[:100]}...'")
        self.api_logger.info(f"allow_llm_to_see_data={allow_llm_to_see_data}")
        
        # Call parent method with allow_llm_to_see_data=True to ensure it's enabled
        result = super().generate_sql(question, allow_llm_to_see_data=True, **kwargs)
        
        self.api_logger.info(f"SQL generated successfully: {result[:100] if result else 'None'}...")
        return result
    
    def extract_sql(self, llm_response: str) -> str:
        """
        Override extract_sql to properly handle intermediate SQL queries.
        Strips 'intermediate_sql' prefix and comment markers.
        
        Args:
            llm_response: Response from LLM that may contain SQL
            
        Returns:
            str: Extracted and cleaned SQL query
        """
        # Call parent method first
        sql = super().extract_sql(llm_response)
        
        # Clean up intermediate_sql prefix if present
        cleaned_sql = sql.strip()
        
        # Remove "intermediate_sql" prefix if present
        if cleaned_sql.startswith('intermediate_sql'):
            lines = cleaned_sql.split('\n')
            cleaned_sql = '\n'.join(line for line in lines if not line.strip().startswith('intermediate_sql')).strip()
        
        # Remove comment markers
        lines = cleaned_sql.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            # Skip comment-only lines with intermediate_sql
            if stripped.startswith('--') and 'intermediate_sql' in stripped.lower():
                continue
            # Remove inline comments
            if '--' in line:
                comment_pos = line.find('--')
                if line[:comment_pos].count("'") % 2 == 0:  # Not inside a string
                    line = line[:comment_pos].rstrip()
            cleaned_lines.append(line)
        cleaned_sql = '\n'.join(cleaned_lines).strip()
        
        # Remove multi-line comments
        while '/*' in cleaned_sql and '*/' in cleaned_sql:
            start = cleaned_sql.find('/*')
            end = cleaned_sql.find('*/', start)
            if end != -1:
                cleaned_sql = cleaned_sql[:start] + cleaned_sql[end+2:].strip()
            else:
                break
        
        self.api_logger.info(f"Extracted SQL (cleaned): {cleaned_sql[:100]}...")
        return cleaned_sql.strip()
    
    def run_sql(self, sql: str, **kwargs) -> AnyType:
        """
        Override to add comprehensive logging for SQL execution using SQLite.
        Also handles intermediate SQL queries by stripping comment prefixes.
        """
        start_time = time.time()
        
        # Clean up SQL: remove "intermediate_sql" prefix and other comment markers
        # Handle cases where LLM prepends "intermediate_sql" as a comment
        cleaned_sql = sql.strip()
        
        # Remove "intermediate_sql" prefix if present (can be on its own line or as a comment)
        if cleaned_sql.startswith('intermediate_sql'):
            # Remove the prefix line
            lines = cleaned_sql.split('\n')
            cleaned_sql = '\n'.join(line for line in lines if not line.strip().startswith('intermediate_sql')).strip()
        
        # Remove SQL comment markers (-- and /* */)
        # Remove single-line comments
        lines = cleaned_sql.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip lines that are just comments
            stripped = line.strip()
            if stripped.startswith('--') and 'intermediate_sql' in stripped.lower():
                continue
            # Remove inline comments that start with --
            if '--' in line:
                comment_pos = line.find('--')
                # Check if it's not inside a string
                if line[:comment_pos].count("'") % 2 == 0:
                    line = line[:comment_pos].rstrip()
            cleaned_lines.append(line)
        cleaned_sql = '\n'.join(cleaned_lines).strip()
        
        # Remove multi-line comments
        while '/*' in cleaned_sql and '*/' in cleaned_sql:
            start = cleaned_sql.find('/*')
            end = cleaned_sql.find('*/', start)
            if end != -1:
                cleaned_sql = cleaned_sql[:start] + cleaned_sql[end+2:].strip()
            else:
                break
        
        self.sql_logger.info(f"Starting SQL execution: '{cleaned_sql[:100]}...'")
        
        # Format SQL for better readability in logs
        sql_lines = cleaned_sql.split('\n')
        formatted_sql = '\n'.join(f"  {line}" for line in sql_lines)
        self.sql_logger.info(f"Executing SQL:\n{formatted_sql}")
        
        try:
            import pandas as pd

            sqlite_env_path = os.getenv('SQLITE_DB_PATH', 'database/water_data.db')
            project_root = Path(__file__).resolve().parent.parent
            sqlite_path = Path(sqlite_env_path)
            if not sqlite_path.is_absolute():
                sqlite_path = (project_root / sqlite_path).resolve()

            if not sqlite_path.exists():
                raise FileNotFoundError(
                    f"SQLite database not found at: {sqlite_path}. "
                    "Please run database/csv_ingestion.py to create it."
                )

            with sqlite3.connect(str(sqlite_path)) as conn:
                conn.row_factory = sqlite3.Row
                result = pd.read_sql_query(cleaned_sql, conn)
            
            duration = time.time() - start_time
            
            self.sql_logger.info(f"SQL execution completed in {duration:.2f}s")
            self.sql_logger.info(f"Query returned {result.shape[0]} rows and {result.shape[1]} columns")
            
            if not result.empty:
                sample_data = result.head(3).to_dict('records')
                self.sql_logger.info(f"Sample data: {json.dumps(sample_data, indent=2, default=str)}")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.sql_logger.error(f"SQL execution failed after {duration:.2f}s: {str(e)}")
            self.sql_logger.error(f"Failed SQL:\n{formatted_sql}")
            raise
    
    def generate_summary(self, question: str = None, df: AnyType = None, **kwargs) -> str:
        """
        Generate natural language summary from query results.
        
        Args:
            question: Original question
            df: DataFrame with query results
            **kwargs: Additional arguments
            
        Returns:
            str: Natural language summary
        """
        if df is None or df.empty:
            if question:
                return f"Based on the question '{question}', no data was found matching the criteria."
            return "No data available to summarize."
        
        try:
            import pandas as pd
            
            # Prepare data summary for the LLM
            data_summary = {
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': list(df.columns),
                'numeric_columns': list(df.select_dtypes(include=['number']).columns),
            }
            
            # Get key statistics for numeric columns
            stats = {}
            numeric_cols = df.select_dtypes(include=['number']).columns
            for col in numeric_cols[:10]:  # Limit to first 10 numeric columns
                if df[col].notna().any():
                    stats[col] = {
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'mean': float(df[col].mean()),
                        'sum': float(df[col].sum()) if len(df) > 0 else 0
                    }
            
            # Prepare sample data (limit to avoid token limits)
            if len(df) <= 10:
                sample_data = df.to_dict('records')
            else:
                sample_data = df.head(10).to_dict('records')
            
            # Create prompt for descriptive summary
            system_prompt = """You are an expert data analyst specializing in water utility financial and operational data. 
Your task is to provide clear, descriptive summaries that explain what the data means in business context, 
not just list statistics. Write in a natural, conversational tone that helps users understand the insights."""
            
            user_prompt = f"""Based on the following query results, provide a descriptive summary that explains what the data means.

Question: {question if question else 'Not provided'}

Query Results:
- Number of rows: {data_summary['row_count']}
- Columns: {', '.join(data_summary['columns'])}
"""
            
            if stats:
                user_prompt += "\nKey Statistics:\n"
                for col, values in stats.items():
                    user_prompt += f"- {col}: min={values['min']:.2f}, max={values['max']:.2f}, mean={values['mean']:.2f}"
                    if values['sum'] != 0:
                        user_prompt += f", total={values['sum']:.2f}"
                    user_prompt += "\n"
            
            user_prompt += f"\nSample Data:\n{json.dumps(sample_data, indent=2, default=str)}"
            
            user_prompt += """

Please provide a descriptive summary that:
1. Answers the question in natural language
2. Explains what the data means in business context
3. Highlights key insights and patterns
4. Uses clear, professional language
5. Avoids just listing statistics - instead, explain what they mean

Keep the summary concise but informative (2-4 sentences for simple queries, up to a paragraph for complex ones)."""
            
            # Generate descriptive summary using OpenAI
            try:
                prompt_messages = [
                    self.system_message(system_prompt),
                    self.user_message(user_prompt)
                ]
                
                # Use the same model as configured for SQL generation (default to gpt-4o-mini)
                model = self.config.get('model', 'gpt-4o-mini') if self.config else 'gpt-4o-mini'
                
                summary = self.submit_prompt(
                    prompt_messages,
                    model=model,
                    temperature=0.7
                )
                
                if summary and summary.strip():
                    return summary.strip()
                else:
                    # Fallback to basic summary if LLM fails
                    return self._generate_fallback_summary(question, df, stats)
                    
            except Exception as llm_error:
                self.api_logger.warning(f"LLM summary generation failed, using fallback: {str(llm_error)}")
                return self._generate_fallback_summary(question, df, stats)
            
        except Exception as e:
            self.api_logger.error(f"Error generating summary: {str(e)}")
            return f"Summary generation failed: {str(e)}"
    
    def _generate_fallback_summary(self, question: str = None, df: AnyType = None, stats: dict = None) -> str:
        """
        Generate a basic fallback summary when LLM is unavailable.
        
        Args:
            question: Original question
            df: DataFrame with query results
            stats: Pre-computed statistics dictionary
            
        Returns:
            str: Basic summary
        """
        import pandas as pd
        
        summary_parts = []
        
        if question:
            summary_parts.append(f"Based on the question '{question}':")
        
        summary_parts.append(f"The query returned {len(df)} row(s) with {len(df.columns)} column(s).")
        
        if stats:
            summary_parts.append("\nKey findings:")
            for col, values in list(stats.items())[:5]:  # Limit to first 5
                if 'total' in values and values['total'] != 0:
                    summary_parts.append(f"  - Total {col}: {values['total']:.2f}")
                elif 'mean' in values:
                    summary_parts.append(f"  - Average {col}: {values['mean']:.2f}")
        
        return "\n".join(summary_parts)
    
    def get_training_data(self, **kwargs):
        """
        Get all training data from the vector store.
        Required abstract method implementation.
        
        Returns:
            pd.DataFrame: Training data with columns [id, question, content, training_data_type]
        """
        try:
            import pandas as pd
            # Use parent class method from PineconeVectorStore
            return super().get_training_data(**kwargs)
        except Exception as e:
            self.api_logger.error(f"Error getting training data: {str(e)}")
            import pandas as pd
            return pd.DataFrame(columns=["id", "question", "content", "training_data_type"])
    
    def remove_training_data(self, id: str, **kwargs) -> bool:
        """
        Remove training data by ID.
        Required abstract method implementation.
        
        Args:
            id: Document ID to remove
            **kwargs: Additional arguments
            
        Returns:
            bool: True if removal was successful
        """
        try:
            # Use parent class method from PineconeVectorStore
            return super().remove_training_data(id, **kwargs)
        except Exception as e:
            self.api_logger.error(f"Error removing training data: {str(e)}")
            return False

