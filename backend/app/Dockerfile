#It instructs Docker Engine to use official python:3.10 as the base image
FROM python:3.10

# Install supervisor
RUN apt-get update && apt-get install -y supervisor --no-install-recommends && rm -rf /var/lib/apt/lists/*

#It creates a working directory(app) for the Docker image and container
WORKDIR /usr/src

#It copies the framework and the dependencies for the FastAPI application into the working directory
COPY requirements.txt .

# Supervisord configuration
COPY supervisord.conf /etc/supervisor

RUN pip install --upgrade pip

#It will install the framework and the dependencies in the `requirements.txt` file.
RUN pip install -r requirements.txt
#It will copy the remaining files and the source code from host folder to the `app` container working directory
COPY . .

# set environment variables
ENV PYTHONPATH=/usr/src

#It will expose the FastAPI application on port `8000` inside the container
EXPOSE 8000

#It is the command that will start and run the FastAPI application container
CMD sh "./app/daemon.sh"

