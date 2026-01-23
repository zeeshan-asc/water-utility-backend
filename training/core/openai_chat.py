"""
OpenAI Chat integration for Vanna AI.

This class handles communication with OpenAI's chat completion API.
"""

import os
from typing import Any, Dict, Optional, List
from openai import OpenAI
from vanna.base import VannaBase


class OpenAI_Chat(VannaBase):
    """
    OpenAI Chat integration for Vanna AI.
    This class handles communication with OpenAI's chat completion API.
    """
    
    def __init__(self, client: Optional[OpenAI] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize OpenAI Chat client.
        
        Args:
            client: Optional pre-configured OpenAI client
            config: Optional configuration dictionary
        """
        VannaBase.__init__(self, config=config)
        
        # Default parameters - can be overridden using config
        self.temperature = 0.7
        if config and "temperature" in config:
            self.temperature = config["temperature"]
        
        # Deprecated config keys - raise helpful errors
        if config:
            if "api_type" in config:
                raise Exception(
                    "Passing api_type is now deprecated. Please pass an OpenAI client instead."
                )
            if "api_base" in config:
                raise Exception(
                    "Passing api_base is now deprecated. Please pass an OpenAI client instead."
                )
            if "api_version" in config:
                raise Exception(
                    "Passing api_version is now deprecated. Please pass an OpenAI client instead."
                )
        
        # Initialize OpenAI client
        if client is not None:
            self.client = client
            return
        if config is None and client is None:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            return
        if config and "api_key" in config:
            self.client = OpenAI(api_key=config["api_key"])
    
    def system_message(self, message: str) -> Dict[str, str]:
        """Create a system message."""
        return {"role": "system", "content": message}
    
    def user_message(self, message: str) -> Dict[str, str]:
        """Create a user message."""
        return {"role": "user", "content": message}
    
    def assistant_message(self, message: str) -> Dict[str, str]:
        """Create an assistant message."""
        return {"role": "assistant", "content": message}
    
    def submit_prompt(self, prompt: List[Dict[str, str]], **kwargs) -> str:
        """
        Submit a prompt to OpenAI's chat completion API.
        
        Args:
            prompt: List of message dictionaries
            **kwargs: Additional arguments (model, engine, etc.)
            
        Returns:
            str: The response content from the API
        """
        if prompt is None:
            raise Exception("Prompt is None")
        if len(prompt) == 0:
            raise Exception("Prompt is empty")
        
        # Count the number of tokens in the message log
        # Use 4 as an approximation for the number of characters per token
        num_tokens = 0
        for message in prompt:
            num_tokens += len(message["content"]) / 4
        
        # Determine which model/engine to use
        if kwargs.get("model", None) is not None:
            model = kwargs.get("model")
            response = self.client.chat.completions.create(
                model=model,
                messages=prompt,
                stop=None,
                temperature=self.temperature,
            )
        elif kwargs.get("engine", None) is not None:
            engine = kwargs.get("engine")
            response = self.client.chat.completions.create(
                engine=engine,
                messages=prompt,
                stop=None,
                temperature=self.temperature,
            )
        elif self.config is not None and "engine" in self.config:
            response = self.client.chat.completions.create(
                engine=self.config["engine"],
                messages=prompt,
                stop=None,
                temperature=self.temperature,
            )
        elif self.config is not None and "model" in self.config:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=prompt,
                stop=None,
                temperature=self.temperature,
            )
        else:
            # Default model selection based on token count
            if num_tokens > 3500:
                model = "gpt-3.5-turbo-16k"
            else:
                model = "gpt-3.5-turbo"
            response = self.client.chat.completions.create(
                model=model,
                messages=prompt,
                stop=None,
                temperature=self.temperature,
            )
        
        # Find the first response from the chatbot that has text in it
        for choice in response.choices:
            if "text" in choice:
                return choice.text
        
        # If no response with text is found, return the first response's content
        return response.choices[0].message.content

