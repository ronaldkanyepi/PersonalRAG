# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


EXPOSE 7860

# Run Chainlit on app.py
CMD ["chainlit", "run", "main.py", "--host", "0.0.0.0", "--port", "7860"]
