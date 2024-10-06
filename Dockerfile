# Use a base Python image
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project directory into the container
COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for the Flask app
EXPOSE 8000

# Run the Flask app using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
