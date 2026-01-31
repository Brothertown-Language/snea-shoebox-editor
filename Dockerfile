# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Create a non-privileged user
RUN groupadd -r snea
RUN useradd -r -g snea -d /home/snea -m -s /sbin/nologin snea

# Set the working directory in the container
WORKDIR /app
RUN chown snea:snea /app

# Install dependencies for uv installer
RUN apt-get update
RUN apt-get install -y --no-install-recommends curl ca-certificates
RUN rm -rf /var/lib/apt/lists/*

# Install uv
ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod +x /install.sh
RUN /install.sh
RUN rm /install.sh
ENV PATH="/root/.local/bin:${PATH}"

# Install project dependencies
COPY pyproject.toml .
RUN uv pip install --system -e .

# Copy the rest of the application
COPY --chown=snea:snea . /app
RUN chown -R snea:snea /app

# Switch to the non-privileged user
USER snea

# Add user's local bin to PATH
ENV PATH="/home/snea/.local/bin:${PATH}"

# Expose the port Solara runs on
EXPOSE 8765

# Command to run Solara
CMD ["solara", "run", "src/frontend/app.py", "--host", "0.0.0.0", "--port", "8765"]
