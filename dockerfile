# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .

# Copy apt requirements

RUN pip install --no-cache-dir -r requirements.txt

# Copy the src directory into the container
COPY src/ .

# Expose port 8071
EXPOSE 8071

# Command to run the application
CMD ["python3", "src/app.py"]
