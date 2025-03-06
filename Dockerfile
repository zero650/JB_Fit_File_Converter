# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install dependencies and set working directory
WORKDIR /app
COPY requirements.txt .
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the application code
COPY . .

# Make port 5500 available to the world outside this container
EXPOSE 5500

# Run the command to start the development server when the container launches
CMD ["python3", "fit_to_db.py"]