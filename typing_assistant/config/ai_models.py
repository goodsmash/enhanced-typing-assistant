"""AI Models configuration and management."""

from dataclasses import dataclass
from typing import Dict, Optional, List

@dataclass
class ModelCharacteristics:
    strengths: List[str]
    best_for: List[str]
    limitations: List[str]
    avg_response_time: float  # in seconds

@dataclass
class ModelLimits:
    tokens_per_minute: int
    requests_per_minute: int
    tokens_per_day: Optional[int] = None
    requests_per_day: Optional[int] = None
    max_tokens: int = 4096  # Default token limit

@dataclass
class ModelPricing:
    input_price_per_1k: float  # Price per 1K input tokens
    output_price_per_1k: float  # Price per 1K output tokens

# OpenAI Models Configuration
OPENAI_MODELS = {
    'gpt-4-turbo-preview': {
        'limits': ModelLimits(
            tokens_per_minute=30000,
            requests_per_minute=500,
            tokens_per_day=90000,
            max_tokens=128000
        ),
        'pricing': ModelPricing(
            input_price_per_1k=0.01,
            output_price_per_1k=0.03
        ),
        'characteristics': ModelCharacteristics(
            strengths=[
                "Most advanced reasoning",
                "Best understanding of context",
                "Excellent writing quality"
            ],
            best_for=[
                "Complex text analysis",
                "Academic writing",
                "Technical documentation"
            ],
            limitations=[
                "Higher cost",
                "May be slower than other models"
            ],
            avg_response_time=2.5
        )
    },
    'gpt-3.5-turbo': {
        'limits': ModelLimits(
            tokens_per_minute=200000,
            requests_per_minute=500,
            tokens_per_day=2000000,
            max_tokens=4096
        ),
        'pricing': ModelPricing(
            input_price_per_1k=0.0005,
            output_price_per_1k=0.0015
        ),
        'characteristics': ModelCharacteristics(
            strengths=[
                "Fast response time",
                "Good general purpose",
                "Cost effective"
            ],
            best_for=[
                "Quick corrections",
                "Simple rewrites",
                "Basic grammar fixes"
            ],
            limitations=[
                "Less nuanced understanding",
                "May miss complex context"
            ],
            avg_response_time=1.0
        )
    }
}

# Anthropic (Claude) Models Configuration
CLAUDE_MODELS = {
    'claude-3-opus-20240229': {
        'limits': ModelLimits(
            tokens_per_minute=5000,
            requests_per_minute=5,
            max_tokens=200000
        ),
        'pricing': ModelPricing(
            input_price_per_1k=0.015,
            output_price_per_1k=0.075
        ),
        'characteristics': ModelCharacteristics(
            strengths=[
                "Excellent comprehension",
                "Very long context window",
                "Strong analytical skills"
            ],
            best_for=[
                "Long document analysis",
                "Research writing",
                "Complex editing tasks"
            ],
            limitations=[
                "Higher cost",
                "Limited requests per minute"
            ],
            avg_response_time=3.0
        )
    },
    'claude-3-sonnet-20240229': {
        'limits': ModelLimits(
            tokens_per_minute=5000,
            requests_per_minute=5,
            max_tokens=200000
        ),
        'pricing': ModelPricing(
            input_price_per_1k=0.003,
            output_price_per_1k=0.015
        ),
        'characteristics': ModelCharacteristics(
            strengths=[
                "Good balance of speed and quality",
                "Large context window",
                "Cost effective for longer texts"
            ],
            best_for=[
                "General writing tasks",
                "Content editing",
                "Document review"
            ],
            limitations=[
                "Less powerful than Opus",
                "Limited requests per minute"
            ],
            avg_response_time=2.0
        )
    }
}

# Task-specific model recommendations
TASK_MODEL_RECOMMENDATIONS = {
    'grammar': ['gpt-3.5-turbo', 'claude-3-sonnet-20240229'],
    'spelling': ['gpt-3.5-turbo', 'claude-3-sonnet-20240229'],
    'style': ['gpt-4-turbo-preview', 'claude-3-opus-20240229'],
    'rewrite': ['gpt-4-turbo-preview', 'claude-3-opus-20240229'],
    'analysis': ['claude-3-opus-20240229', 'gpt-4-turbo-preview'],
    'summary': ['claude-3-sonnet-20240229', 'gpt-3.5-turbo']
}

class TokenUsageTracker:
    """Track token usage and costs across different models."""
    
    def __init__(self):
        self.usage = {
            'total_tokens': 0,
            'total_cost': 0.0,
            'models': {}
        }
        
    def track_usage(self, model: str, input_tokens: int, output_tokens: int) -> Dict:
        """Track usage for a specific model and return cost details."""
        if model.startswith('gpt'):
            model_config = OPENAI_MODELS.get(model)
        else:
            model_config = CLAUDE_MODELS.get(model)
            
        if not model_config:
            raise ValueError(f"Unknown model: {model}")
            
        pricing = model_config['pricing']
        
        # Calculate costs
        input_cost = (input_tokens / 1000) * pricing.input_price_per_1k
        output_cost = (output_tokens / 1000) * pricing.output_price_per_1k
        total_cost = input_cost + output_cost
        
        # Update tracking
        if model not in self.usage['models']:
            self.usage['models'][model] = {
                'input_tokens': 0,
                'output_tokens': 0,
                'total_cost': 0.0
            }
            
        self.usage['models'][model]['input_tokens'] += input_tokens
        self.usage['models'][model]['output_tokens'] += output_tokens
        self.usage['models'][model]['total_cost'] += total_cost
        
        self.usage['total_tokens'] += (input_tokens + output_tokens)
        self.usage['total_cost'] += total_cost
        
        return {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost
        }
    
    def get_usage_report(self) -> Dict:
        """Get a detailed usage report."""
        return self.usage.copy()
    
    def reset_usage(self):
        """Reset all usage statistics."""
        self.usage = {
            'total_tokens': 0,
            'total_cost': 0.0,
            'models': {}
        }
