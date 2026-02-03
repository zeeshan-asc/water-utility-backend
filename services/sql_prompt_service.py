"""
SQL Prompt Service for Vanna AI.

This service provides custom SQL prompt generation with full control over the prompt structure.
Follows Single Responsibility Principle by focusing solely on prompt construction.
"""

from typing import List, Dict, Any, Optional
import logging


class SQLPromptService:
    """
    Service for generating SQL prompts for LLM.
    
    Provides full control over prompt structure while maintaining compatibility
    with Vanna's expected format.
    
    Follows Single Responsibility Principle by focusing solely on prompt construction.
    """
    
    def __init__(
        self,
        dialect: str = "SQLite",
        max_tokens: int = 14000,
        expertise_label: Optional[str] = None,
    ):
        """
        Initialize SQL Prompt Service.
        
        Args:
            dialect: SQL dialect (e.g., "SQLite", "PostgreSQL")
            max_tokens: Maximum tokens for prompt construction
        """
        self.logger = logging.getLogger('vanna.api')
        self.dialect = dialect
        self.max_tokens = max_tokens
        self.static_documentation = ""
        if expertise_label:
            self.expertise_label = expertise_label
        else:
            article = "an" if dialect[:1].lower() in "aeiou" else "a"
            self.expertise_label = f"{article} {dialect} expert"
        
        self.logger.info("=== SQLPromptService INITIALIZED ===")
        self.logger.info(f"Dialect: {self.dialect}")
        self.logger.info(f"Max tokens: {self.max_tokens}")
        self.logger.info(f"Expertise label: {self.expertise_label}")
    
    def set_static_documentation(self, documentation: str) -> None:
        """
        Set static documentation that will always be included in prompts.
        
        Args:
            documentation: Static documentation text
        """
        self.static_documentation = documentation
    
    def str_to_approx_token_count(self, text: str) -> int:
        """
        Approximate token count for text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            int: Approximate token count
        """
        # Simple approximation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def get_initial_system_prompt(self) -> str:
        """
        Get the initial system prompt for SQL generation.
        
        Returns:
            str: Initial system prompt
        """
        return (
            f"You are {self.expertise_label}. "
            "Please help to generate a SQL query to answer the question. "
            "IMPORTANT: All financial currency values in the database (such as Revenue, Expense, Budget, Debt, etc.) are represented in Millions of US Dollars ($M). For example, a value of 29.33 represents $29.33 Million. "
            "Your response should ONLY be based on the given context and follow the response guidelines and format instructions. "
        )
    
    def get_response_guidelines(self) -> str:
        """
        Get the response guidelines section of the prompt.
        
        Returns:
            str: Response guidelines text
        """
        return (
            "===Response Guidelines \n"
            "1. If the provided context is sufficient, please generate a valid SQL query without any explanations for the question. \n"
            "2. If the provided context is almost sufficient but requires knowledge of a specific string in a particular column, please generate an intermediate SQL query to find the distinct strings in that column. Prepend the query with a comment saying intermediate_sql \n"
            "3. If the provided context is insufficient, please explain why it can't be generated. \n"
            "4. Please use the most relevant table(s). \n"
            "5. If the question has been asked and answered before, please repeat the answer exactly as it was given before. \n"
            "6. Please do not use any emojis in your response. \n"
            "7. Always give type SQL in response and never give type text \n"
            f"8. Ensure that the output SQL is {self.dialect}-compliant and executable, and free of syntax errors. \n"
        )
    
    def add_ddl_to_prompt(
        self, 
        initial_prompt: str, 
        ddl_list: List[str]
    ) -> str:
        """
        Add DDL (table schemas) to the prompt.
        
        Args:
            initial_prompt: Current prompt text
            ddl_list: List of DDL statements
            
        Returns:
            str: Updated prompt with DDL section
        """
        if len(ddl_list) > 0:
            self.logger.info(f"Adding {len(ddl_list)} DDL statements to prompt")
            initial_prompt += "\n===Tables \n"
            
            ddl_added = 0
            for ddl in ddl_list:
                current_tokens = self.str_to_approx_token_count(initial_prompt)
                ddl_tokens = self.str_to_approx_token_count(ddl)
                
                if current_tokens + ddl_tokens < self.max_tokens:
                    initial_prompt += f"{ddl}\n\n"
                    ddl_added += 1
                else:
                    self.logger.warning(f"DDL truncated due to token limit. Added {ddl_added}/{len(ddl_list)} DDL statements")
                    break
            
            if ddl_added == len(ddl_list):
                self.logger.info(f"Successfully added all {ddl_added} DDL statements")
        else:
            self.logger.info("No DDL statements to add")
        
        return initial_prompt
    
    def add_documentation_to_prompt(
        self,
        initial_prompt: str,
        documentation_list: List[str]
    ) -> str:
        """
        Add documentation/context to the prompt.
        
        Args:
            initial_prompt: Current prompt text
            documentation_list: List of documentation strings
            
        Returns:
            str: Updated prompt with documentation section
        """
        if len(documentation_list) > 0:
            self.logger.info(f"Adding {len(documentation_list)} documentation items to prompt")
            initial_prompt += "\n===Additional Context \n\n"
            
            docs_added = 0
            for documentation in documentation_list:
                current_tokens = self.str_to_approx_token_count(initial_prompt)
                doc_tokens = self.str_to_approx_token_count(documentation)
                
                if current_tokens + doc_tokens < self.max_tokens:
                    initial_prompt += f"{documentation}\n\n"
                    docs_added += 1
                else:
                    self.logger.warning(f"Documentation truncated due to token limit. Added {docs_added}/{len(documentation_list)} items")
                    break
            
            if docs_added == len(documentation_list):
                self.logger.info(f"Successfully added all {docs_added} documentation items")
        else:
            self.logger.info("No documentation items to add")
        
        return initial_prompt
    
    def build_sql_prompt(
        self,
        question: str,
        ddl_list: List[str],
        doc_list: List[str],
        question_sql_list: List[Dict[str, str]],
        initial_prompt: Optional[str] = None,
        user_message_func: Any = None,
        assistant_message_func: Any = None,
        system_message_func: Any = None,
        filter_data: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, str]]:
        """
        Build complete SQL generation prompt.
        
        This is the main method that constructs the entire prompt in Vanna's message format.
        
        Args:
            question: User's question
            ddl_list: List of DDL statements
            doc_list: List of documentation strings
            question_sql_list: List of similar question-SQL pairs
            initial_prompt: Optional custom initial prompt (overrides default)
            user_message_func: Function to format user messages
            assistant_message_func: Function to format assistant messages
            system_message_func: Function to format system messages
            filter_data: Optional filter extraction data
            history: Optional conversation history
            
        Returns:
            List[Dict[str, str]]: Message log in Vanna format
        """
        self.logger.info("=== SQLPromptService.build_sql_prompt() STARTED ===")
        self.logger.info(f"Building SQL prompt for question: '{question[:100]}{'...' if len(question) > 100 else ''}'")
        
        # Start with initial prompt
        if initial_prompt is None:
            initial_prompt = self.get_initial_system_prompt()
        
        # Add static documentation if configured
        if self.static_documentation:
            doc_list = doc_list + [self.static_documentation]
        
        # Add DDL section
        initial_prompt = self.add_ddl_to_prompt(initial_prompt, ddl_list)
        
        # Add documentation section
        initial_prompt = self.add_documentation_to_prompt(initial_prompt, doc_list)
        
        # Add response guidelines
        initial_prompt += self.get_response_guidelines()
        
        # Build message log
        message_log = [system_message_func(initial_prompt)]
        
        # Add few-shot examples
        for example in question_sql_list:
            if example and "question" in example and "sql" in example:
                message_log.append(user_message_func(example["question"]))
                message_log.append(assistant_message_func(example["sql"]))
        
        # Add conversation history
        if history:
            self.logger.info(f"Adding {len(history)} history turns to prompt")
            for turn in history:
                prev_q = turn.get('question')
                # Use SQL if available, otherwise use summary/text as the assistant's previous "answer"
                prev_a = turn.get('sql') or turn.get('summary') or turn.get('text')
                
                if prev_q and prev_a:
                    message_log.append(user_message_func(str(prev_q)))
                    message_log.append(assistant_message_func(str(prev_a)))
        
        # Add the actual user question
        message_log.append(user_message_func(question))
        
        # Log token usage
        total_tokens = sum(self.str_to_approx_token_count(msg.get("content", "")) for msg in message_log)
        self.logger.info(f"Total prompt tokens (approx): {total_tokens} / {self.max_tokens} max")
        
        if total_tokens > self.max_tokens:
            self.logger.warning(f"WARNING: Prompt exceeds max_tokens limit! ({total_tokens} > {self.max_tokens})")
        
        self.logger.info("=== SQLPromptService.build_sql_prompt() COMPLETED ===")
        
        return message_log

