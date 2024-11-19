"""AI Service Manager for handling multiple AI models and tracking usage."""

import logging
from typing import Dict, Optional, Tuple, List
import tiktoken
from openai import OpenAI, AsyncOpenAI
from anthropic import Anthropic
from ..config.ai_models import (
    TokenUsageTracker, OPENAI_MODELS, CLAUDE_MODELS,
    TASK_MODEL_RECOMMENDATIONS
)

logger = logging.getLogger(__name__)

class AIServiceManager:
    """Manages AI services, model selection, and usage tracking."""
    
    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.anthropic_client = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        self.async_openai_client = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
        self.token_tracker = TokenUsageTracker()
        self.current_model = 'gpt-3.5-turbo'  # Default model
        
        # Initialize tokenizers
        self.tokenizers = {}
        if self.openai_client:
            for model in OPENAI_MODELS:
                try:
                    self.tokenizers[model] = tiktoken.encoding_for_model(model)
                except KeyError:
                    self.tokenizers[model] = tiktoken.get_encoding("cl100k_base")
    
    def get_available_models(self) -> List[str]:
        """Get list of available models based on API keys."""
        models = []
        if self.openai_client:
            models.extend(OPENAI_MODELS.keys())
        if self.anthropic_client:
            models.extend(CLAUDE_MODELS.keys())
        return models
    
    def get_model_info(self, model: str) -> Dict:
        """Get detailed information about a specific model."""
        model_config = OPENAI_MODELS.get(model) or CLAUDE_MODELS.get(model)
        if not model_config:
            raise ValueError(f"Unknown model: {model}")
        return {
            'limits': model_config['limits'].__dict__,
            'pricing': model_config['pricing'].__dict__,
            'characteristics': model_config['characteristics'].__dict__
        }
    
    def get_recommended_models(self, task: str) -> List[str]:
        """Get recommended models for a specific task."""
        available_models = self.get_available_models()
        recommended = TASK_MODEL_RECOMMENDATIONS.get(task, [])
        return [model for model in recommended if model in available_models]
    
    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """Count tokens for a given text and model."""
        model = model or self.current_model
        
        if model.startswith('gpt'):
            tokenizer = self.tokenizers.get(model)
            if not tokenizer:
                tokenizer = tiktoken.get_encoding("cl100k_base")
            return len(tokenizer.encode(text))
        else:
            # Claude uses a different tokenizer, approximate for now
            return len(text.split()) * 1.3  # Rough approximation
    
    def select_model(self, text_length: int, task: str = 'grammar', 
                    quality: str = 'standard', cost_sensitive: bool = False) -> str:
        """Select the most appropriate model based on requirements."""
        token_estimate = self.count_tokens(text_length * 'x')
        available_models = self.get_available_models()
        
        # Get task-specific recommendations
        recommended_models = self.get_recommended_models(task)
        
        # Filter models by token limit
        valid_models = []
        for model in recommended_models:
            if model in available_models:
                model_config = OPENAI_MODELS.get(model) or CLAUDE_MODELS.get(model)
                if token_estimate <= model_config['limits'].max_tokens:
                    valid_models.append(model)
        
        if not valid_models:
            # Fallback to any available model that can handle the token count
            for model in available_models:
                model_config = OPENAI_MODELS.get(model) or CLAUDE_MODELS.get(model)
                if token_estimate <= model_config['limits'].max_tokens:
                    valid_models.append(model)
        
        if not valid_models:
            raise ValueError("No suitable model found for the given text length")
        
        # Select based on quality and cost preferences
        if cost_sensitive:
            # Sort by cost and select cheapest
            return min(valid_models, key=lambda m: self.estimate_cost(text_length * 'x', m)['estimated_total_cost'])
        elif quality == 'high':
            # Prefer more capable models
            preferred = ['claude-3-opus-20240229', 'gpt-4-turbo-preview']
            for model in preferred:
                if model in valid_models:
                    return model
        
        # Default to first recommended model
        return valid_models[0]
    
    async def process_text(self, text: str, task: str = 'correction', 
                          quality: str = 'standard') -> Tuple[str, Dict]:
        """Process text using the appropriate AI model."""
        model = self.select_model(len(text), task, quality)
        input_tokens = self.count_tokens(text, model)
        
        try:
            if model.startswith('gpt'):
                response = await self.async_openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful writing assistant."},
                        {"role": "user", "content": f"Task: {task}\nText: {text}"}
                    ]
                )
                result = response.choices[0].message.content
                output_tokens = self.count_tokens(result, model)
                
            else:  # Claude models
                response = await self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=self.count_tokens(text) * 2,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Task: {task}\nText: {text}"
                        }
                    ]
                )
                result = response.content[0].text
                output_tokens = self.count_tokens(result, model)
            
            # Track usage and costs
            usage_info = self.token_tracker.track_usage(model, input_tokens, output_tokens)
            
            return result, {
                'model': model,
                'usage': usage_info,
                'total_cost': usage_info['total_cost']
            }
            
        except Exception as e:
            logger.error(f"Error processing text with {model}: {str(e)}")
            raise
    
    def get_usage_statistics(self) -> Dict:
        """Get current usage statistics."""
        return self.token_tracker.get_usage_report()
    
    def reset_usage_statistics(self):
        """Reset usage statistics."""
        self.token_tracker.reset_usage()
    
    def estimate_cost(self, text: str, model: Optional[str] = None) -> Dict:
        """Estimate cost for processing text."""
        model = model or self.current_model
        input_tokens = self.count_tokens(text, model)
        estimated_output_tokens = input_tokens * 1.5  # Rough estimation
        
        if model.startswith('gpt'):
            model_config = OPENAI_MODELS[model]
        else:
            model_config = CLAUDE_MODELS[model]
            
        pricing = model_config['pricing']
        input_cost = (input_tokens / 1000) * pricing.input_price_per_1k
        output_cost = (estimated_output_tokens / 1000) * pricing.output_price_per_1k
        
        return {
            'model': model,
            'estimated_input_tokens': input_tokens,
            'estimated_output_tokens': estimated_output_tokens,
            'estimated_input_cost': input_cost,
            'estimated_output_cost': output_cost,
            'estimated_total_cost': input_cost + output_cost,
            'characteristics': model_config['characteristics'].__dict__
        }
