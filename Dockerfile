# Base Image: Lightweight Python 3.11
FROM python:3.11-slim

# Set Working Directory
WORKDIR /app

# Install System Dependencies (if any required for c2pa-python/cryptography)
# e.g., build-essential, libssl-dev. For now, slim usually suffices for wheels.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy Dependencies
COPY requirements.txt .

# Install Python Packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy Application Code
COPY trust_engine/ ./trust_engine/
COPY sample_signed.jpg . 

# Create Storage Directories
RUN mkdir -p storage/creds storage/uploads

# Expose API Port
EXPOSE 8080

# Run the Server
CMD ["uvicorn", "trust_engine.main:app", "--host", "0.0.0.0", "--port", "8080"]
