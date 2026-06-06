"""
LLM Chatbot Implementation
Conversational AI chatbot with memory and prompt engineering
"""
import os
import logging
from typing import List, Dict, Any, Optional
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.chains import ConversationChain
from langchain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain.schema import HumanMessage, AIMessage

logger = logging.getLogger(__name__)


class Chatbot:
    """Conversational AI Chatbot"""
    
    def __init__(
        self,
        llm_provider: str = "openai",
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        memory_type: str = "buffer"
    ):
        """
        Initialize chatbot
        
        Args:
            llm_provider: LLM provider ("openai" or "huggingface")
            model_name: Model name
            temperature: Sampling temperature
            memory_type: Memory type ("buffer" or "summary")
        """
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.temperature = temperature
        self.memory_type = memory_type
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Initialize memory
        self.memory = self._initialize_memory()
        
        # Initialize conversation chain
        self.conversation = self._initialize_conversation()
    
    def _initialize_llm(self):
        """Initialize LLM"""
        if self.llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            
            if "gpt" in self.model_name.lower():
                return ChatOpenAI(
                    openai_api_key=api_key,
                    model_name=self.model_name,
                    temperature=self.temperature
                )
            else:
                return OpenAI(
                    openai_api_key=api_key,
                    model_name=self.model_name,
                    temperature=self.temperature
                )
        else:
            # HuggingFace implementation would go here
            raise NotImplementedError("HuggingFace LLM not yet implemented")
    
    def _initialize_memory(self):
        """Initialize conversation memory"""
        if self.memory_type == "buffer":
            return ConversationBufferMemory(
                return_messages=True,
                memory_key="history"
            )
        elif self.memory_type == "summary":
            return ConversationSummaryMemory(
                llm=self.llm,
                return_messages=True,
                memory_key="history"
            )
        else:
            raise ValueError(f"Unknown memory type: {self.memory_type}")
    
    def _initialize_conversation(self):
        """Initialize conversation chain"""
        # Create prompt template
        if isinstance(self.llm, ChatOpenAI):
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful AI assistant. Answer questions clearly and concisely."),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}")
            ])
        else:
            prompt = PromptTemplate(
                input_variables=["history", "input"],
                template="""You are a helpful AI assistant. Answer questions clearly and concisely.

Conversation history:
{history}

Human: {input}
Assistant:"""
            )
        
        # Create conversation chain
        conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt,
            verbose=True
        )
        
        return conversation
    
    def chat(self, message: str) -> str:
        """
        Send a message to the chatbot
        
        Args:
            message: User message
            
        Returns:
            Bot response
        """
        try:
            response = self.conversation.predict(input=message)
            return response
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"Error: {str(e)}"
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
        logger.info("Memory cleared")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history
        
        Returns:
            List of conversation messages
        """
        history = []
        if hasattr(self.memory, "chat_memory"):
            messages = self.memory.chat_memory.messages
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    history.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    history.append({"role": "assistant", "content": msg.content})
        return history


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Initialize chatbot
    chatbot = Chatbot(
        llm_provider="openai",
        model_name="gpt-3.5-turbo",
        memory_type="buffer"
    )
    
    # Test conversation
    print("Chatbot initialized. Type 'quit' to exit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "quit":
            break
        
        response = chatbot.chat(user_input)
        print(f"Bot: {response}")

