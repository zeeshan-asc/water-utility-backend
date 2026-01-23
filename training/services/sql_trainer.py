"""
SQL trainer service for Vanna AI.
Handles training with SQL query examples and question-SQL pairs.

Follows Single Responsibility Principle by focusing solely on SQL training.
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from ..core.training_interface import BaseTrainer


class SQLTrainer(BaseTrainer):
    """
    Trainer for SQL queries and question-SQL pairs.
    
    This class handles training Vanna AI with example SQL queries and 
    natural language question-SQL query pairs for improved accuracy.
    """
    
    def __init__(self, training_data_file: Optional[str] = None) -> None:
        """
        Initialize the SQL trainer.
        
        Args:
            training_data_file: Optional path to JSON file containing training data
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.sql_examples: List[str] = []
        self.question_sql_pairs: List[Tuple[str, str]] = []
        
        # Load training data from file if provided
        if training_data_file:
            self.load_training_data_from_json(training_data_file)
    
    def add_sql_example(self, sql_query: str) -> None:
        """
        Add a SQL query example for training.
        
        Args:
            sql_query: The SQL query to add as a training example
        """
        if self.validate_sql_query(sql_query):
            self.sql_examples.append(sql_query.strip())
            self.logger.info(f"Added SQL example: {sql_query[:50]}...")
        else:
            self.logger.warning(f"Invalid SQL query not added: {sql_query[:50]}...")
    
    def add_question_sql_pair(self, question: str, sql_query: str) -> None:
        """
        Add a question-SQL pair for training.
        
        Args:
            question: Natural language question
            sql_query: Corresponding SQL query
        """
        if self.validate_sql_query(sql_query) and question.strip():
            self.question_sql_pairs.append((question.strip(), sql_query.strip()))
            self.logger.info(f"Added question-SQL pair: '{question[:30]}...' -> '{sql_query[:30]}...'")
        else:
            self.logger.warning(f"Invalid question-SQL pair not added")
    
    def load_training_data_from_json(self, file_path: str) -> bool:
        """
        Load training data from a JSON file containing question-SQL pairs.
        
        Args:
            file_path: Path to JSON file with training data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Handle different JSON structures
            training_pairs = []
            
            # Check if it's a list of pairs
            if isinstance(data, list):
                training_pairs = data
            # Check if it's an object with 'training_pairs' key
            elif isinstance(data, dict) and 'training_pairs' in data:
                training_pairs = data['training_pairs']
            else:
                self.logger.error(f"Invalid JSON structure in {file_path}")
                return False
            
            # Load question-SQL pairs
            loaded_count = 0
            for pair in training_pairs:
                if isinstance(pair, dict) and 'question' in pair and 'sql' in pair:
                    self.add_question_sql_pair(pair['question'], pair['sql'])
                    loaded_count += 1
                else:
                    self.logger.warning(f"Skipping invalid training pair: {pair}")
            
            self.logger.info(f"Loaded {loaded_count} question-SQL pairs from {file_path}")
            return loaded_count > 0
            
        except FileNotFoundError:
            self.logger.error(f"Training data file not found: {file_path}")
            return False
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in {file_path}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error loading training data from {file_path}: {e}")
            return False
    
    def validate_sql_query(self, sql_query: str) -> bool:
        """
        Basic validation of SQL query.
        
        Args:
            sql_query: The SQL query to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not sql_query or not sql_query.strip():
            return False
        
        # Basic SQL validation - check for common SQL keywords
        sql_upper = sql_query.upper().strip()
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'WITH']
        
        return any(sql_upper.startswith(keyword) for keyword in sql_keywords)
    
    def train(self, vanna_instance) -> bool:
        """
        Train the Vanna instance with SQL data.
        
        Args:
            vanna_instance: The Vanna AI instance to train
            
        Returns:
            bool: True if training was successful, False otherwise
        """
        try:
            # Validate Vanna instance
            if not self.validate_vanna_instance(vanna_instance):
                self.logger.error("Invalid Vanna instance provided")
                return False
            
            success_count = 0
            total_count = 0
            
            # Train with SQL examples
            for sql_query in self.sql_examples:
                try:
                    self.logger.info(f"Training with SQL example: {sql_query[:50]}...")
                    vanna_instance.add_sql(sql_query)
                    success_count += 1
                except Exception as e:
                    self.logger.error(f"Error training SQL example: {e}")
                total_count += 1
            
            # Train with question-SQL pairs
            for question, sql_query in self.question_sql_pairs:
                try:
                    self.logger.info(f"Training with Q&A pair: '{question[:30]}...'")
                    vanna_instance.add_question_sql(question, sql_query)
                    success_count += 1
                except Exception as e:
                    self.logger.error(f"Error training question-SQL pair: {e}")
                total_count += 1
            
            if total_count == 0:
                self.logger.warning("No SQL training data available")
                return True  # Not an error, just no data to train
            
            self.logger.info(f"SQL training completed: {success_count}/{total_count} successful")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Error during SQL training: {e}")
            return False
    
    def get_training_data_type(self) -> str:
        """
        Get the type of training data this trainer handles.
        
        Returns:
            str: The training data type identifier
        """
        return "sql"
    
    def clear_training_data(self) -> None:
        """Clear all stored training data."""
        self.sql_examples.clear()
        self.question_sql_pairs.clear()
        self.logger.info("Cleared all SQL training data")
    
    def get_training_data_summary(self) -> Dict[str, int]:
        """
        Get a summary of current training data.
        
        Returns:
            Dict with counts of different training data types
        """
        return {
            "sql_examples": len(self.sql_examples),
            "question_sql_pairs": len(self.question_sql_pairs),
            "total_items": len(self.sql_examples) + len(self.question_sql_pairs)
        }




