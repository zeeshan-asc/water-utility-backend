"""
Abstract interface for Vanna AI training services.
Implements Interface Segregation Principle by defining focused training contracts.
"""

from abc import ABC, abstractmethod
from typing import Any, Protocol


class VannaTrainerProtocol(Protocol):
    """Protocol defining the interface for Vanna AI trainers."""
    
    def train(self, vanna_instance) -> bool:
        """
        Train the Vanna instance with specific data type.
        
        Args:
            vanna_instance: The Vanna AI instance to train
            
        Returns:
            bool: True if training was successful, False otherwise
        """
        ...


class BaseTrainer(ABC):
    """
    Abstract base class for all Vanna AI trainers.
    Implements Dependency Inversion Principle by depending on abstractions.
    """
    
    def __init__(self) -> None:
        """Initialize the trainer."""
        pass
    
    @abstractmethod
    def train(self, vanna_instance) -> bool:
        """
        Train the Vanna instance with specific data.
        
        Args:
            vanna_instance: The Vanna AI instance to train
            
        Returns:
            bool: True if training was successful, False otherwise
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement train method")
    
    @abstractmethod
    def get_training_data_type(self) -> str:
        """
        Get the type of training data this trainer handles.
        
        Returns:
            str: The training data type identifier
        """
        raise NotImplementedError("Subclasses must implement get_training_data_type method")
    
    def validate_vanna_instance(self, vanna_instance) -> bool:
        """
        Validate that the Vanna instance is properly configured.
        
        Args:
            vanna_instance: The Vanna AI instance to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return vanna_instance is not None and hasattr(vanna_instance, 'train')




