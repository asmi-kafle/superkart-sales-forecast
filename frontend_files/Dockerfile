FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy frontend application and dependencies
COPY . .

# Install Streamlit and requests
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Expose default Streamlit port 8501
EXPOSE 8501

# Run Streamlit app accessible externally
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
