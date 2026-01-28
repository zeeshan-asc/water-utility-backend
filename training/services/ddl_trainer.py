"""
DDL trainer service for Vanna AI.
Handles training with Data Definition Language (DDL) statements.

Follows Single Responsibility Principle by focusing solely on DDL training.
"""

import logging
from pathlib import Path
from typing import Optional
from ..core.training_interface import BaseTrainer


class DDLTrainer(BaseTrainer):
    """
    Trainer for DDL (Data Definition Language) statements.
    
    This class handles loading and training Vanna AI with database schema definitions.
    """
    
    def __init__(self, ddl_file_path: Optional[str] = None) -> None:
        """
        Initialize the DDL trainer.
        
        Args:
            ddl_file_path: Optional path to DDL file. If None, uses default schema location.
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.ddl_file_path = ddl_file_path or "schema/water_data.sql"
    
    def load_ddl_from_file(self, file_path: str) -> str:
        """
        Load DDL content from a SQL file.
        
        Args:
            file_path: Path to the SQL file containing DDL statements
            
        Returns:
            str: The DDL content as a string
            
        Raises:
            FileNotFoundError: If the DDL file doesn't exist
            IOError: If there's an error reading the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                ddl_content = file.read().strip()
                self.logger.info(f"Successfully loaded DDL from {file_path}")
                return ddl_content
        except FileNotFoundError:
            self.logger.error(f"DDL file not found: {file_path}")
            raise
        except IOError as e:
            self.logger.error(f"Error reading DDL file {file_path}: {e}")
            raise
    
    def validate_ddl_content(self, ddl_content: str) -> bool:
        """
        Validate that the DDL content is not empty and contains CREATE TABLE statement.
        
        Args:
            ddl_content: The DDL content to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not ddl_content or not ddl_content.strip():
            self.logger.error("DDL content is empty")
            return False
        
        # Basic validation - check for CREATE TABLE statement
        if "CREATE TABLE" not in ddl_content.upper():
            self.logger.error("DDL content does not contain CREATE TABLE statement")
            return False
        
        return True
    
    def train(self, vanna_instance) -> bool:
        """
        Train the Vanna instance with DDL data.
        
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
            
            # Load DDL content
            ddl_content = self.load_ddl_from_file(self.ddl_file_path)
            
            # Validate DDL content
            if not self.validate_ddl_content(ddl_content):
                return False
            
            # Train Vanna with DDL
            self.logger.info("Training Vanna with DDL data...")
            vanna_instance.add_ddl(ddl_content)
            
            self.logger.info("DDL training completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during DDL training: {e}")
            return False
    
    def get_training_data_type(self) -> str:
        """
        Get the type of training data this trainer handles.
        
        Returns:
            str: The training data type identifier
        """
        return "ddl"
    
    def set_ddl_file_path(self, file_path: str) -> None:
        """
        Set a new DDL file path.
        
        Args:
            file_path: Path to the DDL file
        """
        self.ddl_file_path = file_path
        self.logger.info(f"DDL file path updated to: {file_path}")
    
    def get_ddl_file_path(self) -> str:
        """
        Get the current DDL file path.
        
        Returns:
            str: Current DDL file path
        """
        return self.ddl_file_path









