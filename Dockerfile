# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
RUN pip install uv

# Copy the current directory contents into the container at /app
COPY . /app

# Install project dependencies
RUN uv pip install --system -e .

# Expose the port Solara runs on
EXPOSE 8765

# Command to run Solara
CMD ["solara", "run", "src/frontend/app.py", "--host", "0.0.0.0", "--port", "8765"]
