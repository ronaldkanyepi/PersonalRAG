FROM python:3.10-slim

# Create a non-root user for security
RUN useradd -m -u 1000 user

USER user

# Ensure pip-installed binaries in ~/.local/bin are accessible
ENV PATH="/home/user/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY --chown=user ./requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user . /app

EXPOSE 7860

CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]
