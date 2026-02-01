# Copyright (c) 2026 Brothertown Language
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# --- ROOT SETUP PHASE ---
# Only system packages and user configuration here.

# Create a non-privileged user
RUN groupadd -r snea
RUN useradd -r -g snea -d /home/snea -m -s /sbin/nologin snea

# Set the working directory in the container
WORKDIR /app

# Pre-allocate and set ownership
RUN chown snea:snea /app

# Install dependencies for uv installer (discrete steps)
RUN apt-get update
RUN apt-get install -y --no-install-recommends curl
RUN apt-get install -y --no-install-recommends ca-certificates

# Cleanup apt cache
RUN rm -rf /var/lib/apt/lists/*

# --- UNPRIVILEGED USER PHASE ---
USER snea
ENV HOME=/home/snea
ENV PATH="/home/snea/.local/bin:${PATH}"
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Install uv (As snea)
ADD --chown=snea:snea https://astral.sh/uv/install.sh /home/snea/install.sh
RUN chmod +x /home/snea/install.sh
RUN /home/snea/install.sh
RUN rm /home/snea/install.sh

# Install project dependencies using uv-managed project environment (.venv)
COPY --chown=snea:snea pyproject.toml .
COPY --chown=snea:snea uv.lock* .
RUN uv sync

# Copy the rest of the application
COPY --chown=snea:snea . /app

# Expose the port Streamlit runs on
EXPOSE 8501

# Default command uses uv to target the active project environment
CMD ["uv", "run", "--no-sync", "--active", "python3", "-m", "streamlit", "run", "src/frontend/app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
