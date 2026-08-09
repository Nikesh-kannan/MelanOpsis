FROM python:3.10-slim

WORKDIR /app

# Install OpenCV system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements & install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code into container
COPY src/backend /app

# Ensure data and model directories exist
RUN mkdir -p /app/data/images /app/models

# Expose Hugging Face default port 7860
EXPOSE 7860

# Start FastAPI app on port 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
