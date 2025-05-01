# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM --platform=linux/amd64 python:3.11-slim

# Set the working directory
# WORKDIR .

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port that Streamlit will run on
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "streamlit_app_msds.py", "--server.port=8501", "--server.address=0.0.0.0"]