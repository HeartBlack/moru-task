FROM python:3.11.3-slim-buster

# Set work directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && cat apt_requirements.txt | xargs apt -y --no-install-recommends install \
    && rm -rf /var/lib/apt/lists/* \
    && apt autoremove \
    && apt autoclean

# Install Python dependencies
RUN pip install --upgrade pip
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# Copy project files
COPY . /usr/src/app/

# Set entrypoint script permissions
RUN chmod +x /usr/src/app/entrypoint.sh
RUN chmod -R 777 /usr/src/app
# RUN flask db init
# RUN flask db upgrade

# Set the entrypoint
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
