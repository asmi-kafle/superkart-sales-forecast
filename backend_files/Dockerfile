FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all backend files (app.py, requirements.txt, superkart_model.joblib)
COPY . .

# Install pinned Python dependencies without cache to minimize image size
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Expose port 7860 and launch Flask via Gunicorn with 4 worker processes
EXPOSE 7860
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
