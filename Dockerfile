# Use an official Python runtime as the base image
FROM python:3

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the project requirements file to the working directory
COPY requirements.txt /app

# Install project dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the project code to the working directory
COPY . /app

# Expose the Django development server port
#EXPOSE 8000

# Run the Django development server
ENTRYPOINT ["sh","scripts/docker-entrypoint-dev.sh"]
