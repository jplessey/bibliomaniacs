FROM python:3.8-slim-buster

# Working Directory
WORKDIR /app

# Copy source code to working directory
COPY app.py /app/
COPY database_setup.py /app/
COPY templates /app/templates
COPY static /app/static
COPY requirements.txt /app/
COPY Dockerfile /app/

# Install packages from requirements.txt
# hadolint ignore=DL3013
RUN pip install --upgrade pip &&\
    pip install --trusted-host pypi.python.org -r requirements.txt
    
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    make \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*    

# Expose port 80
EXPOSE 80

# Run app.py at container launch
CMD ["python", "app.py"]