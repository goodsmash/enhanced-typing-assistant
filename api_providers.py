import abc
import openai
from typing import Dict, List, Optional

class BaseAIProvider(abc.ABC):
    """Base class for AI text correction providers"""
    
    @abc.abstractmethod
    def correct_text(self, text: str, prompt: str) -> str:
        """Correct the given text using the AI model"""
        pass
        
    @abc.abstractmethod
    def get_available_models(self) -> List[str]:
        """Return a list of available models for this provider"""
        pass

class OpenAIProvider(BaseAIProvider):
    """OpenAI API provider implementation"""
    
    AVAILABLE_MODELS = {
        "GPT-4": "gpt-4",
        "GPT-4 Turbo": "gpt-4-turbo-preview",
        "GPT-3.5 Turbo": "gpt-3.5-turbo",
        "GPT-3.5": "gpt-3.5-turbo-instruct"
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key
        
    def correct_text(self, text: str, prompt: str) -> str:
        response = openai.ChatCompletion.create(
            model=self.current_model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
        
    def get_available_models(self) -> List[str]:
        return list(self.AVAILABLE_MODELS.keys())
        
    def set_model(self, model_name: str):
        """Set the current model to use"""
        self.current_model = self.AVAILABLE_MODELS.get(model_name, "gpt-3.5-turbo")

class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude API provider implementation"""
    
    AVAILABLE_MODELS = {
        "Claude 3 Opus": "claude-3-opus-20240229",
        "Claude 3 Sonnet": "claude-3-sonnet-20240229",
        "Claude 2.1": "claude-2.1",
        "Claude 2": "claude-2"
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("Please install anthropic package to use Claude models")
        
    def correct_text(self, text: str, prompt: str) -> str:
        message = self.client.messages.create(
            model=self.current_model,
            system=prompt,
            messages=[{"role": "user", "content": text}]
        )
        return message.content[0].text
        
    def get_available_models(self) -> List[str]:
        return list(self.AVAILABLE_MODELS.keys())
        
    def set_model(self, model_name: str):
        """Set the current model to use"""
        self.current_model = self.AVAILABLE_MODELS.get(model_name, "claude-2")

class ProviderFactory:
    """Factory class to create AI providers"""
    
    PROVIDERS = {
        "OpenAI": OpenAIProvider,
        "Anthropic": AnthropicProvider
    }
    
    @staticmethod
    def create_provider(provider_name: str, api_key: str) -> BaseAIProvider:
        """Create and return an instance of the specified provider"""
        provider_class = ProviderFactory.PROVIDERS.get(provider_name)
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}")
        return provider_class(api_key)
        
    @staticmethod
    def get_available_providers() -> List[str]:
        """Return a list of available provider names"""
        return list(ProviderFactory.PROVIDERS.keys())