FROM python:3.13-slim

# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures that Python output is sent straight to terminal (no buffering)
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements/base.txt /app/requirements/base.txt
RUN pip install --upgrade pip && pip install -r requirements/base.txt

# Copy project files into the container
COPY . /app

# Default command to run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
