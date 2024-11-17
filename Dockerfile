# Build stage for React frontend
FROM node:20-slim as frontend-builder

# Set working directory
WORKDIR /app/web

# Copy package files
COPY web/package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source
COPY web/ ./

# Build React app
RUN npm run build

# Build stage for Python backend
FROM python:3.12-slim as backend-builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python application
COPY typing_assistant/ ./typing_assistant/

# Final stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy Python dependencies from backend builder
COPY --from=backend-builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

# Copy application from backend builder
COPY --from=backend-builder /app/typing_assistant/ ./typing_assistant/

# Copy built React app from frontend builder
COPY --from=frontend-builder /app/web/build/ ./web/build/

# Copy additional files
COPY requirements.txt .

# Create non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expose ports
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Start the FastAPI server
CMD ["python", "-m", "uvicorn", "typing_assistant.api.gender_inclusive_api:app", "--host", "0.0.0.0", "--port", "8000"]
