FROM mcr.microsoft.com/devcontainers/python:3.12

ENV PYTHONUNBUFFERED=1

RUN sudo apt-get update && \
    sudo apt-get install -y curl

RUN pip install --upgrade pip

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH=/root/.local/bin:$PATH
RUN apt-get update && \
    apt-get install -y portaudio19-dev python3-dev gcc && \
    rm -rf /var/lib/apt/lists/*