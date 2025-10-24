# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Make port 8000 available to the world outside this container
# (Change this if your app runs on a different port)
EXPOSE 5033

# Define the command to run your app
# This command is for an ASGI app (like FastAPI) using Gunicorn
# 'main:app' means it expects a file named 'main.py' with an app variable named 'app'
# If your file is 'app.py', you should change 'main:app' to 'app:app'
CMD ["gunicorn", "app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]