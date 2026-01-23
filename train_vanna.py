"""
Vanna AI Training Script for Water Utility Data

This script trains a Vanna AI model with DDL, documentation, and question-SQL pairs.
Follows SOLID principles with dependency injection and modular architecture.

Usage:
    python train_vanna.py              # Add to existing training data
    python train_vanna.py --fresh-start # Clear all data and retrain
    python train_vanna.py --help        # Show help

Environment Variables Required:
    OPENAI_API_KEY: OpenAI API key
    PINECONE_API_KEY: Pinecone API key
    PINECONE_ENVIRONMENT: Pinecone environment/region (optional, defaults to us-east-1)
    PINECONE_INDEX_NAME: Pinecone index name (optional, defaults to aquasentinel-index)
"""

import os
import sys
import logging
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Import training services
from training.core.training_interface import BaseTrainer
from training.services.ddl_trainer import DDLTrainer
from training.services.documentation_trainer import DocumentationTrainer
from training.services.sql_trainer import SQLTrainer

# Import Vanna instance
from core.custom_vanna import MyVanna


class VannaTrainingOrchestrator:
    """
    Orchestrates the training of Vanna AI with multiple data sources.
    
    Follows Single Responsibility Principle by focusing on training coordination.
    Uses Dependency Injection for flexibility and testability.
    """
    
    def __init__(self, vanna_instance) -> None:
        """
        Initialize the training orchestrator.
        
        Args:
            vanna_instance: Configured Vanna AI instance
        """
        self.vanna_instance = vanna_instance
        self.logger = logging.getLogger(__name__)
        self.trainers: List[BaseTrainer] = []
        
        # Initialize trainers with dependency injection
        self._initialize_trainers()
    
    def _initialize_trainers(self) -> None:
        """Initialize all training services."""
        try:
            project_root = Path(__file__).resolve().parent
            
            # DDL Trainer
            ddl_trainer = DDLTrainer(str(project_root / "schema" / "water_data.sql"))
            self.trainers.append(ddl_trainer)
            
            # Documentation Trainer
            doc_trainer = DocumentationTrainer()
            self.trainers.append(doc_trainer)
            
            # SQL Trainer with training data from JSON file
            sql_trainer = SQLTrainer(str(project_root / "training_sql_data.json"))
            self.trainers.append(sql_trainer)
            
            self.logger.info(f"Initialized {len(self.trainers)} trainers")
            
        except Exception as e:
            self.logger.error(f"Error initializing trainers: {e}")
            raise
    
    def add_trainer(self, trainer: BaseTrainer) -> None:
        """
        Add a custom trainer to the orchestrator.
        
        Args:
            trainer: Training service implementing BaseTrainer interface
        """
        if not isinstance(trainer, BaseTrainer):
            raise ValueError("Trainer must implement BaseTrainer interface")
        
        self.trainers.append(trainer)
        self.logger.info(f"Added custom trainer: {trainer.get_training_data_type()}")
    
    def train_all(self, skip_on_error: bool = True) -> bool:
        """
        Execute training with all configured trainers.
        
        Args:
            skip_on_error: If True, continue training with other trainers if one fails
            
        Returns:
            bool: True if at least one trainer succeeded, False if all failed
        """
        if not self.trainers:
            self.logger.error("No trainers configured")
            return False
        
        success_count = 0
        total_count = len(self.trainers)
        
        self.logger.info(f"Starting training with {total_count} trainers...")
        
        for trainer in self.trainers:
            try:
                trainer_type = trainer.get_training_data_type()
                self.logger.info(f"Training with {trainer_type} trainer...")
                
                if trainer.train(self.vanna_instance):
                    success_count += 1
                    self.logger.info(f"{trainer_type} training completed successfully")
                else:
                    self.logger.error(f"{trainer_type} training failed")
                    if not skip_on_error:
                        return False
                        
            except Exception as e:
                self.logger.error(f"Error in {trainer.get_training_data_type()} trainer: {e}")
                if not skip_on_error:
                    return False
        
        self.logger.info(f"Training completed: {success_count}/{total_count} trainers successful")
        return success_count > 0
    
    def get_training_summary(self) -> dict:
        """
        Get a summary of the training data that will be used.
        
        Returns:
            dict: Summary of training data
        """
        summary = {
            "total_trainers": len(self.trainers),
            "trainer_types": [trainer.get_training_data_type() for trainer in self.trainers]
        }
        
        # Add SQL trainer specific summary if available
        for trainer in self.trainers:
            if isinstance(trainer, SQLTrainer):
                summary["sql_training_data"] = trainer.get_training_data_summary()
        
        return summary


class ConfigurationManager:
    """
    Manages configuration and environment variables for Vanna training.
    
    Follows Single Responsibility Principle by handling only configuration.
    """
    
    def __init__(self) -> None:
        """Initialize configuration manager."""
        self.logger = logging.getLogger(__name__)
        load_dotenv()
    
    def validate_environment(self) -> bool:
        """
        Validate that all required environment variables are set.
        
        Returns:
            bool: True if all required variables are present
        """
        required_vars = [
            'OPENAI_API_KEY',
            'PINECONE_API_KEY'
        ]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.logger.error(f"Missing required environment variables: {missing_vars}")
            return False
        
        return True
    
    def get_vanna_config(self) -> dict:
        """
        Get Vanna configuration from environment variables.
        
        Returns:
            dict: Configuration dictionary for Vanna initialization
        """
        return {
            'model': 'gpt-4o-mini',
            'temperature': 0.7,
        }


def setup_logging() -> None:
    """Configure logging for the training script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('vanna_training.log')
        ]
    )


def display_training_data_summary(vanna_instance) -> None:
    """
    Display a summary of the training data in the model.
    
    Args:
        vanna_instance: The trained Vanna instance
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Retrieving training data summary...")
        training_data = vanna_instance.get_training_data()
        
        if training_data is not None and not training_data.empty:
            print("\n" + "="*50)
            print("TRAINING DATA SUMMARY")
            print("="*50)
            print(f"Total training records: {len(training_data)}")
            
            # Group by training data type
            if 'training_data_type' in training_data.columns:
                type_counts = training_data['training_data_type'].value_counts()
                print("\nTraining data by type:")
                for data_type, count in type_counts.items():
                    print(f"  {data_type}: {count} records")
            
            print("\nFirst few training records:")
            print(training_data.head().to_string())
            print("="*50)
        else:
            print("No training data found in the model.")
            
    except Exception as e:
        logger.error(f"Error retrieving training data summary: {e}")


def main() -> int:
    """
    Main training execution function.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting Vanna AI training process...")
        
        # Check for command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "--fresh-start":
                logger.info("Fresh start mode: Will clear existing training data first")
                fresh_start = True
            elif sys.argv[1] == "--help":
                print("\nVanna AI Training Script")
                print("Usage:")
                print("  python train_vanna.py              # Add to existing training data")
                print("  python train_vanna.py --fresh-start # Clear all data and retrain")
                print("  python train_vanna.py --help        # Show this help")
                print("\nTo manage existing training data, use: python training_data_manager.py")
                return 0
            else:
                logger.warning(f"Unknown argument: {sys.argv[1]}. Use --help for usage info.")
                fresh_start = False
        else:
            fresh_start = False
        
        # Validate configuration
        config_manager = ConfigurationManager()
        if not config_manager.validate_environment():
            logger.error("Environment validation failed. Please check your .env file.")
            return 1
        
        # Initialize Vanna
        vanna_config = config_manager.get_vanna_config()
        logger.info(f"Initializing Vanna with config: {vanna_config}")
        vanna_instance = MyVanna(config=vanna_config)
        
        if not vanna_instance:
            logger.error("Failed to initialize Vanna AI")
            return 1
        
        logger.info("Vanna AI instance initialized successfully")
        
        # Handle fresh start if requested
        if fresh_start:
            logger.info("Clearing existing training data...")
            try:
                training_data = vanna_instance.get_training_data()
                if training_data is not None and len(training_data) > 0:
                    logger.info(f"Found {len(training_data)} existing records to remove")
                    for index, row in training_data.iterrows():
                        vanna_instance.remove_training_data(id=row['id'])
                    logger.info("All existing training data cleared")
                else:
                    logger.info("No existing training data found")
            except Exception as e:
                logger.error(f"Error clearing training data: {e}")
                return 1
        
        # Create training orchestrator
        orchestrator = VannaTrainingOrchestrator(vanna_instance)
        
        # Display training summary
        training_summary = orchestrator.get_training_summary()
        logger.info(f"Training summary: {training_summary}")
        
        # Execute training
        success = orchestrator.train_all(skip_on_error=True)
        
        if success:
            logger.info("Training completed successfully!")
            
            # Display training data summary
            display_training_data_summary(vanna_instance)
            
            print("\nTraining completed! Your Vanna AI model is now ready to use.")
            print("You can now run your main application to start querying the database.")
            
            if not fresh_start:
                print("\nNOTE: Training data was ADDED to existing data.")
                print("To start fresh next time, use: python train_vanna.py --fresh-start")
            
            return 0
        else:
            logger.error("Training failed!")
            return 1
            
    except Exception as e:
        logger.error(f"Unexpected error during training: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
