import os
import asyncio
from dataclasses import dataclass
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class ModerationResult:
    flagged: bool
    categories: Dict[str, bool]
    category_scores: Dict[str, float]
    error: Optional[str] = None

class ContentModerator:
    def __init__(self):
        self.client = OpenAI()
        self.default_thresholds = {
            'hate': 0.5,
            'hate/threatening': 0.5,
            'harassment': 0.5,
            'self-harm': 0.5,
            'sexual': 0.5,
            'sexual/minors': 0.5,
            'violence': 0.5,
            'violence/graphic': 0.5
        }
        
    async def check_content(self, text: str, custom_thresholds: Dict[str, float] = None) -> ModerationResult:
        """
        Check if the content is appropriate using OpenAI's moderation API.
        
        Args:
            text (str): The text to check
            custom_thresholds (Dict[str, float]): Optional custom thresholds for each category
            
        Returns:
            ModerationResult: Object containing moderation results and any errors
        """
        try:
            # Input validation
            if not text or not isinstance(text, str):
                raise ValueError("Invalid input text")
                
            # Use custom thresholds if provided, otherwise use defaults
            thresholds = custom_thresholds or self.default_thresholds
            
            response = await asyncio.to_thread(
                self.client.moderations.create,
                input=text
            )
            
            # Get the first result
            result = response.results[0]
            
            return ModerationResult(
                flagged=result.flagged,
                categories=result.categories,
                category_scores=result.category_scores
            )
            
        except Exception as e:
            return ModerationResult(
                flagged=True,  # Fail safe: flag content if moderation fails
                categories={},
                category_scores={},
                error=str(e)
            )
            
    def is_safe_content(self, result: ModerationResult, custom_thresholds: Dict[str, float] = None) -> bool:
        """
        Determine if content is safe based on moderation results and thresholds.
        
        Args:
            result (ModerationResult): Results from check_content()
            custom_thresholds (Dict[str, float]): Optional custom thresholds
            
        Returns:
            bool: True if content is safe, False otherwise
        """
        if result.error or not result.category_scores:
            return False
            
        thresholds = custom_thresholds or self.default_thresholds
        
        # Check if any category score exceeds its threshold
        for category, threshold in thresholds.items():
            if category in result.category_scores:
                if result.category_scores[category] > threshold:
                    return False
                    
        return True
        
    def get_violation_details(self, result: ModerationResult, custom_thresholds: Dict[str, float] = None) -> Dict[str, float]:
        """
        Get details about which categories violated thresholds.
        
        Args:
            result (ModerationResult): Results from check_content()
            custom_thresholds (Dict[str, float]): Optional custom thresholds
            
        Returns:
            Dict[str, float]: Dictionary of violated categories and their scores
        """
        if result.error or not result.category_scores:
            return {}
            
        thresholds = custom_thresholds or self.default_thresholds
        violations = {}
        
        for category, threshold in thresholds.items():
            if category in result.category_scores:
                score = result.category_scores[category]
                if score > threshold:
                    violations[category] = score
                    
        return violations
        
    async def cleanup(self):
        """Clean up any resources"""
        pass  # Add cleanup code if needed
