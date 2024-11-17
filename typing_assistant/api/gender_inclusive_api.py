"""FastAPI-based web service for gender-inclusive corrections."""

from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import logging
from pathlib import Path

from ..gec.gender_inclusive import GenderInclusiveCorrector
from ..gec.dictionary import DictionaryManager
from ..gec.correction_result import CorrectionResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Gender-Inclusive Language API",
    description="API for gender-inclusive language corrections in text and code",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class CorrectionRequest(BaseModel):
    """Request model for text correction."""
    text: str = Field(..., description="Text to be corrected")
    context: Optional[Dict] = Field(None, description="Optional context (e.g., file path, language)")
    
class CorrectionResponse(BaseModel):
    """Response model for text correction."""
    original_text: str = Field(..., description="Original input text")
    corrected_text: str = Field(..., description="Corrected text")
    corrections: List[Dict] = Field(..., description="List of corrections made")
    confidence: float = Field(..., description="Confidence score of corrections")

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")

# Dependency for GenderInclusiveCorrector
def get_corrector() -> GenderInclusiveCorrector:
    """Get or create GenderInclusiveCorrector instance."""
    if not hasattr(app.state, "corrector"):
        # Initialize dictionary manager and corrector
        dictionary_manager = DictionaryManager()
        app.state.corrector = GenderInclusiveCorrector(dictionary_manager)
    return app.state.corrector

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check API health status."""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.post("/correct", response_model=CorrectionResponse, tags=["Correction"])
async def correct_text(
    request: CorrectionRequest,
    corrector: GenderInclusiveCorrector = Depends(get_corrector)
):
    """Correct text for gender-inclusive language.
    
    Args:
        request: CorrectionRequest containing text and optional context
        corrector: GenderInclusiveCorrector instance
        
    Returns:
        CorrectionResponse with corrected text and suggestions
    """
    try:
        result = corrector.correct_text(request.text, request.context)
        return {
            "original_text": result.original_text,
            "corrected_text": result.corrected_text,
            "corrections": result.corrections,
            "confidence": result.confidence
        }
    except Exception as e:
        logger.error(f"Error processing correction request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing correction request: {str(e)}"
        )

@app.get("/suggestions", response_model=List[Dict], tags=["Correction"])
async def get_suggestions(
    text: str,
    context: Optional[Dict] = None,
    corrector: GenderInclusiveCorrector = Depends(get_corrector)
):
    """Get gender-inclusive language suggestions without applying corrections.
    
    Args:
        text: Text to analyze
        context: Optional context information
        corrector: GenderInclusiveCorrector instance
        
    Returns:
        List of correction suggestions
    """
    try:
        return corrector.get_correction_suggestions(text, context)
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting suggestions: {str(e)}"
        )

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server."""
    uvicorn.run(app, host=host, port=port)
